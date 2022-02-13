package com.example.cx3004;

import android.app.ProgressDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.os.ParcelUuid;
import android.util.Log;
import android.widget.Toast;

import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.Queue;
import java.util.UUID;

public class BluetoothConnectionService {
    BluetoothPairingPage mBluetoothPairingPage;
    private static BluetoothConnectionService instance;
    private static final String TAG = "DebuggingTag";

    private static final String appName = "CX3004";
    public static final UUID myUUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    private final BluetoothAdapter mBluetoothAdapter;
    Context mContext;

    private AcceptThread mInsecureAcceptThread;

    private ConnectThread mConnectThread;
    private BluetoothDevice mDevice;
    private UUID deviceUUID;
    Intent connectionStatus;

    public static boolean BluetoothConnectionStatus = false;
    private static ConnectedThread mConnectedThread;

    public BluetoothConnectionService(Context context) {
        this.mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        this.mContext = context;
    }

    private class AcceptThread extends Thread {
        private final BluetoothServerSocket ServerSocket;
        private boolean runThread = true;

        public AcceptThread() {
            BluetoothServerSocket tmp = null;

            try {
                tmp = mBluetoothAdapter.listenUsingInsecureRfcommWithServiceRecord(appName, myUUID);
                Log.d(TAG, "Accept Thread: Setting up Server using: " + myUUID);
            } catch (IOException e) {
                Log.e(TAG, "Accept Thread: IOException: " + e.getMessage());
            }
            ServerSocket = tmp;
        }

        public void run() {
            Log.d(TAG, "run: AcceptThread Running. ");
            while (!BluetoothConnectionStatus & runThread){
                BluetoothSocket socket = null;
                try {
                    Log.d(TAG, "run: RFCOM server socket start here...");

                    socket = ServerSocket.accept();
                    Log.d(TAG, "run: RFCOM server socket accepted connection.");
                } catch (IOException e) {
                    Log.e(TAG, "AcceptThread: Failed to accept client socket: " + e.getMessage());
                }
                if (socket != null) {
                    connected(socket, socket.getRemoteDevice());
                    break;
                }
            }
            Log.i(TAG, "END AcceptThread");
        }

        public void cancel() {
            Log.d(TAG, "cancel: Cancelling AcceptThread");

            // stop while loop in run
            runThread = false;

            // close server socket
            try {
                ServerSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "cancel: Failed to close AcceptThread ServerSocket " + e.getMessage());
            }

            // set accept thread to null
            mInsecureAcceptThread = null;
        }
    }

    private class ConnectThread extends Thread {
        private BluetoothSocket mSocket;
        private Queue<ParcelUuid> deviceParcelUUIDs;

        public ConnectThread(BluetoothDevice device, UUID u) {
            Log.d(TAG, "ConnectThread: started.");
            mDevice = device;
            deviceUUID = u;

            deviceParcelUUIDs = new LinkedList<>(Arrays.asList(device.getUuids()));
        }

        public void run() {
            Log.d(TAG, "ConnectThread: Starting run().");

            runDeviceUuidMode();
            //runMyUuidMode();

            Log.d(TAG, "ConnectThread: Exiting run().");
        }

        public void runMyUuidMode(){
            Log.d(TAG, "ConnectThread: Starting runMyUuidMode().");


            attemptConnection(deviceUUID);


            // no uuids left to try in queue, connection to device failed
            if (!BluetoothConnectionStatus){
                try {
                    BluetoothPairingPage mBluetoothPopUpActivity = (BluetoothPairingPage) mContext;
                    mBluetoothPopUpActivity.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            String deviceName = mDevice.getName();
                            deviceName = (deviceName == null) ? mDevice.getAddress() : deviceName;
                            Toast.makeText(mContext,
                                    String.format("Failed to connect to %s. Try initiating connection from %s!", deviceName, deviceName),
                                    Toast.LENGTH_SHORT).show();
                        }
                    });
                } catch (Exception z) {
                    z.printStackTrace();
                }
            }
            Log.d(TAG, "ConnectThread: Exiting runMyUuidMode().");
        }

        public void runDeviceUuidMode(){
            Log.d(TAG, "ConnectThread: Starting runDeviceUuidMode().");

            while (!deviceParcelUUIDs.isEmpty()){
                UUID uuid = deviceParcelUUIDs.remove().getUuid();
                if (attemptConnection(uuid)) break;
            }

            // no uuids left to try in queue, connection to device failed
            if (!BluetoothConnectionStatus){
                try {
                    BluetoothPairingPage mBluetoothPopUpActivity = (BluetoothPairingPage) mContext;
                    mBluetoothPopUpActivity.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(mContext, "Failed to connect to the Device.", Toast.LENGTH_SHORT).show();
                        }
                    });
                } catch (Exception z) {
                    z.printStackTrace();
                }
            }
            Log.d(TAG, "ConnectThread: Exiting runDeviceUuidMode().");
        }

        public boolean attemptConnection(UUID uuid){
            BluetoothSocket tmp = null;
            Log.d(TAG, "RUN: mConnectThread");

            try {
                Log.d(TAG, "ConnectThread: Trying to create InsecureRfcommSocket using UUID: " + uuid);
                tmp = mDevice.createRfcommSocketToServiceRecord(uuid);
            } catch (IOException e) {
                Log.e(TAG, "ConnectThread: Could not create InsecureRfcommSocket " + e.getMessage());
            }
            mSocket = tmp;

            try {
                mSocket.connect();
                Log.d(TAG, "RUN: ConnectThread connected.");
                connected(mSocket, mDevice);
                return true;
            } catch (IOException e) {
                cancel();
                Log.d(TAG, "ConnectThread: could not connect to UUID " + uuid);
            }
            return false;
        }

        public void cancel() {
            // close socket
            Log.d(TAG, "cancel: Closing Client Socket");
            try {
                mSocket.close();
                mSocket = null;
                Log.d(TAG, "ConnectThread: Socket closed.");
            } catch (IOException e) {
                Log.e(TAG, "cancel: Failed to close ConnectThread mSocket " + e.getMessage());
            } catch (NullPointerException e) {
                Log.e(TAG, "ConnectThread: No socket to close: " + e.getMessage());
            }

            // set connect thread to null
            mConnectThread = null;
        }
    }

    public synchronized void startAcceptThread() {
        Log.d(TAG, "START AcceptThread");

//        if (mConnectThread != null) {
//            mConnectThread.cancel();
//            mConnectThread = null;
//        }
        if (mInsecureAcceptThread == null) {
            mInsecureAcceptThread = new AcceptThread();
            mInsecureAcceptThread.start();
        }
    }

    public void startClientThread(BluetoothDevice device, UUID uuid) {
        Log.d(TAG, "startClient: Started.");

        if (mConnectThread == null){
            mConnectThread = new ConnectThread(device, uuid);
            mConnectThread.start();
        }
    }

    private class ConnectedThread extends Thread {
        private final BluetoothSocket mSocket;
        private final InputStream inStream;
        private final OutputStream outStream;

        public ConnectedThread(BluetoothSocket socket) {
            Log.d(TAG, "ConnectedThread: Starting.");

            connectionStatus = new Intent("ConnectionStatus");
            connectionStatus.putExtra("Status", "connected");
            connectionStatus.putExtra("Device", mDevice);
            LocalBroadcastManager.getInstance(mContext).sendBroadcast(connectionStatus);
            BluetoothConnectionStatus = true;

            this.mSocket = socket;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            try {
                tmpIn = mSocket.getInputStream();
                tmpOut = mSocket.getOutputStream();
            } catch (IOException e) {
                e.printStackTrace();
            }

            inStream = tmpIn;
            outStream = tmpOut;
        }

        public void run() {
            byte[] buffer = new byte[1024];
            int bytes;

            while (true) {
                try {
                    bytes = inStream.read(buffer);
                    String incomingmessage = new String(buffer, 0, bytes);
                    Log.d(TAG, "InputStream: " + incomingmessage);

                    Intent incomingMessageIntent = new Intent("incomingMessage");
                    incomingMessageIntent.putExtra("receivedMessage", incomingmessage);

                    LocalBroadcastManager.getInstance(mContext).sendBroadcast(incomingMessageIntent);
                } catch (IOException e) {
                    Log.e(TAG, "ConnectedThread: Error reading input stream. " + e.getMessage());
                    cancel(); // close socket

                    //if (mConnectThread != null) mConnectThread.run();

                    break;
                }
            }
        }

        public void write(byte[] bytes) {
            String text = new String(bytes, Charset.defaultCharset());
            Log.d(TAG, "write: Writing to output stream: " + text);
            try {
                outStream.write(bytes);
            } catch (IOException e) {
                Log.e(TAG, "Error writing to output stream. " + e.getMessage());
            }
        }

        public void cancel() {
            // close input and output streams
            Log.d(TAG, "ConnectedThread: Attempting to close input and output streams.");
            try {
                inStream.close();
                Log.d(TAG, "ConnectedThread: Input stream closed.");
                outStream.close();
                Log.d(TAG, "ConnectedThread: Output stream closed.");
            } catch (IOException e) {
                Log.e(TAG, "ConnectedThread: Failed to close streams: " + e.getMessage());
            }

            // close sockets
            Log.d(TAG, "ConnectedThread: Attempting to close socket.");
            try {
                mSocket.close();
                Log.d(TAG, "ConnectedThread: Socket closed.");
                connectionStatus = new Intent("ConnectionStatus");
                connectionStatus.putExtra("Status", "disconnected");
                connectionStatus.putExtra("Device", mDevice);
                LocalBroadcastManager.getInstance(mContext).sendBroadcast(connectionStatus);
                BluetoothConnectionStatus = false;
            } catch (IOException e) {
                Log.e(TAG, "ConnectedThread: Failed to close mSocket: " + e.getMessage());
            }

            // set connected thread to null
            mConnectedThread = null;
        }
    }

    private void connected(BluetoothSocket mSocket, BluetoothDevice device) {
        Log.d(TAG, "connected: Starting.");
        mDevice = device;
        if (mInsecureAcceptThread != null) mInsecureAcceptThread.cancel();

        mConnectedThread = new ConnectedThread(mSocket);
        mConnectedThread.start();
    }

    public static void write(byte[] out) {
        ConnectedThread tmp;
        Log.d(TAG, "write: Write is called.");
        mConnectedThread.write(out);
    }

    public void stop(){
        if (mConnectedThread != null) mConnectedThread.cancel();
        if (mInsecureAcceptThread != null) mInsecureAcceptThread.cancel();
        if (mConnectThread != null) mConnectThread.cancel();
        Log.d(TAG, "All threads in BluetoothConnectionService have been stopped.");
    }
}
