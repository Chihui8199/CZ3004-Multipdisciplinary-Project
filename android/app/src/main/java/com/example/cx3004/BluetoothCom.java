package com.example.cx3004;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.Charset;

public class BluetoothCom extends Thread {
    private static final String TAG = "BluetoothChat";


    // Declarations
    private static Context myContext;
    private static BluetoothSocket mySocket;
    private static InputStream myInputStream;
    private static OutputStream myOutPutStream;
    private static BluetoothDevice myBtConnectionDevice;


    // To maintain the bluetooth connection, sending the data, and receiving incoming messages
    // through input/output streams.
    public static BluetoothDevice getBluetoothDevice(){
        return myBtConnectionDevice;
    }

    // Start Bluetooth Chat
    public static void startComms(BluetoothSocket socket) {

        Log.d(TAG, "ConnectedThread: Starting");

        mySocket = socket;
        InputStream tempIn = null;
        OutputStream tempOut = null;


        try {
            tempIn = mySocket.getInputStream();
            tempOut = mySocket.getOutputStream();
        } catch (IOException e) {
            e.printStackTrace();
        }
        myInputStream = tempIn;
        myOutPutStream = tempOut;


        // Buffer store for the stream
        byte[] buffer = new byte[1024];

        // Bytes returned from the read()
        int bytes;

        while (true) {
            // Read from the InputStream
            try {
                bytes = myInputStream.read(buffer);
                String incomingMessage = new String(buffer, 0, bytes);
                Log.d(TAG, "InputStream: " + incomingMessage);

                // Broadcast Incoming Message
                Intent incomingMsgIntent = new Intent("IncomingMsg");
                incomingMsgIntent.putExtra("receivingMsg", incomingMessage);
                LocalBroadcastManager.getInstance(myContext).sendBroadcast(incomingMsgIntent);


            } catch (IOException e) {

                // Broadcast Connection Message
                Intent connectionStatusIntent = new Intent("btConnectionStatus");
                connectionStatusIntent.putExtra("ConnectionStatus", "disconnect");
                connectionStatusIntent.putExtra("Device", myBtConnectionDevice);
                LocalBroadcastManager.getInstance(myContext).sendBroadcast(connectionStatusIntent);

                Log.d(TAG, "CHAT SERVICE: Closed!!!");
                e.printStackTrace();
                break;

            } catch (Exception e){
                Log.d(TAG, "CHAT SERVICE: Closed 2!!!: "+ e);
                e.printStackTrace();

            }

        }
    }


    // To write outgoing bluetooth messages
    public static void write(byte[] bytes) {

        String text = new String(bytes, Charset.defaultCharset());
        Log.d(TAG, "Write: Writing to outputstream: " + text);

        try {
            myOutPutStream.write(bytes);
        } catch (Exception e) {
            Log.d(TAG, "Write: Error writing to output stream: " + e.getMessage());
        }
    }


    // To shut down bluetooth connection
    public void cancel() {
        try {
            mySocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }



    // To start Communication
    static void connected(BluetoothSocket mySocket, BluetoothDevice myDevice, Context context) {
        Log.d(TAG, "Connected: Starting");
        myBtConnectionDevice = myDevice;
        myContext = context;
        //Start thread to manage the connection and perform transmissions
        startComms(mySocket);


    }

    /*
        Write to ConnectedThread in an unsynchronised manner
    */
    public static void writeMsg(byte[] out) {

        Log.d(TAG, "write: Write Called.");
        write(out);

    }

}
