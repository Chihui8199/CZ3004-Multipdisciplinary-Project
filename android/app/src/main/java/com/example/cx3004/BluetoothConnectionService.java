package com.example.cx3004;

import android.app.IntentService;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import androidx.annotation.Nullable;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.io.IOException;
import java.util.UUID;

public class BluetoothConnectionService extends IntentService {
    private static final String TAG = "BtService";
    private static final String NAME = "MDPTest";

    private BluetoothDevice mmDevice;
    private BluetoothAdapter mBluetoothAdapter;
    private AcceptThread myAcceptThread;
    private ConnectThread mConnectThread;
    private static final UUID myUUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");
    private UUID deviceUUID;
    Context mContext;


    public BluetoothConnectionService() {
        super("BTService");
    }

    @Override
    protected void onHandleIntent(@Nullable Intent intent) {
        mContext = getApplicationContext();
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        if (intent.getStringExtra("serviceType").equals("listen")) {
            mmDevice = (BluetoothDevice) intent.getExtras().getParcelable("device");
            Log.d(TAG, "Service Handle: startAcceptThread");
            startAcceptThread();
        } else {
            mmDevice = (BluetoothDevice) intent.getExtras().getParcelable("device");
            deviceUUID = (UUID) intent.getSerializableExtra("id");
            Log.d(TAG, "Service Handle: startClientThread "+mmDevice.getName()+" UUID:"+deviceUUID.toString());
            startClient(mmDevice, deviceUUID);
        }
    }

    /**
     * Start the chat service. Specifically start AcceptThread to begin a
     * session in listening (server) mode. Called by the Activity onResume()
     */
    public synchronized void startAcceptThread() {
        Log.d(TAG, "start");

        // Cancel any thread attempting to make a connection
        if (mConnectThread != null) {
            mConnectThread.cancel();
            mConnectThread = null;
        }
        if (myAcceptThread == null) {
            myAcceptThread = new AcceptThread();
            myAcceptThread.start();
        }
    }

    /**
     AcceptThread starts and sits waiting for a connection.
     Then ConnectThread starts and attempts to make a connection with the other devices AcceptThread.
     **/

    public void startClient(BluetoothDevice device,UUID uuid){
        Log.d(TAG, "startClient: Started.");
        mConnectThread = new ConnectThread(device, uuid);
        mConnectThread.start();
    }

    /**
     * Thread acts as server. Listening for connections.
     */
    private class AcceptThread extends Thread {
        private final BluetoothServerSocket mmServerSocket;

        public AcceptThread() {
            // Use a temporary object that is later assigned to mmServerSocket
            // because mmServerSocket is final.
            BluetoothServerSocket tmp = null;
            try {
                // MY_UUID is the app's UUID string, also used by the client code.
                tmp = mBluetoothAdapter.listenUsingRfcommWithServiceRecord(NAME, myUUID);
            } catch (IOException e) {
                Log.e(TAG, "Socket's listen() method failed", e);
            }
            mmServerSocket = tmp;
        }

        public void run() {

            Log.d(TAG, "AcceptThread: Running");

            BluetoothSocket socket;
            Intent connectionStatusIntent;

            try {

                Log.d(TAG, "Run: RFCOM server socket start....");

                // Blocking call which will only return on a successful connection / exception
                socket = mmServerSocket.accept();

                // Broadcast connection message
                connectionStatusIntent = new Intent("btConnectionStatus");
                connectionStatusIntent.putExtra("ConnectionStatus", "connect");
                connectionStatusIntent.putExtra("Device", BluetoothActivity.getBluetoothDevice());
                LocalBroadcastManager.getInstance(mContext).sendBroadcast(connectionStatusIntent);

                // Successfully connected
                Log.d(TAG, "Run: RFCOM server socket accepted connection");

                // Start BluetoothChat
                BluetoothCom.connected(socket, mmDevice, mContext);


            } catch (IOException e) {
                connectionStatusIntent = new Intent("btConnectionStatus");
                connectionStatusIntent.putExtra("ConnectionStatus", "connectionFail");
                connectionStatusIntent.putExtra("Device",  BluetoothActivity.getBluetoothDevice());

                Log.d(TAG, "AcceptThread: Connection Failed ,IOException: " + e.getMessage());
            }

            Log.d(TAG, "Ended AcceptThread");

        }

        // Closes the connect socket and causes the thread to finish.
        public void cancel() {
            Log.d(TAG, "Cancel: Canceling AcceptThread");

            try {
                mmServerSocket.close();
            } catch (IOException e) {
                Log.d(TAG, "Cancel: Closing AcceptThread Failed. " + e.getMessage());
            }
        }
    }


    /**
     * Connect as client
     *
     */
    private class ConnectThread extends Thread {
        private BluetoothSocket mmSocket;

        public ConnectThread(BluetoothDevice device, UUID uuid) {
            Log.d(TAG, "ConnectThread: started.");
            mmDevice = device;
            deviceUUID = uuid;
        }

        public void run() {
            BluetoothSocket temp = null;
            Intent connectionStatusIntent;

            Log.d(TAG, "Run: myConnectThread");

            // BluetoothSocket for connection with given BluetoothDevice
            try {
                Log.d(TAG, "ConnectThread: Trying to create InsecureRFcommSocket to "+mmDevice.getName()+" using UUID: " +
                        myUUID);
                temp = mmDevice.createRfcommSocketToServiceRecord(deviceUUID);
            } catch (IOException e) {

                Log.d(TAG, "ConnectThread: Could not create InsecureRFcommSocket " + e.getMessage());
            }

            mmSocket = temp;

            // Cancel discovery to prevent slow connection
            mBluetoothAdapter.cancelDiscovery();

            try {

                Log.d(TAG, "Connecting to Device: " + mmDevice);
                // Blocking call and will only return on a successful connection / exception
                mmSocket.connect();


                // Broadcast connection message
                connectionStatusIntent = new Intent("btConnectionStatus");
                connectionStatusIntent.putExtra("ConnectionStatus", "connect");
                connectionStatusIntent.putExtra("Device", mmDevice);
                LocalBroadcastManager.getInstance(mContext).sendBroadcast(connectionStatusIntent);

                Log.d(TAG, "run: ConnectThread connected");

                // Start BluetoothChat
                BluetoothCom.connected(mmSocket, mmDevice, mContext);

                // Cancel myAcceptThread for listening
                if (myAcceptThread != null) {
                    myAcceptThread.cancel();
                    myAcceptThread = null;
                }

            } catch (IOException e) {

                // Close socket on error
                try {
                    mmSocket.close();

                    connectionStatusIntent = new Intent("btConnectionStatus");
                    connectionStatusIntent.putExtra("ConnectionStatus", "connectionFail");
                    connectionStatusIntent.putExtra("Device", mmDevice);
                    LocalBroadcastManager.getInstance(mContext).sendBroadcast(connectionStatusIntent);
                    Log.d(TAG, "run: Socket Closed: Connection Failed!! " + e.getMessage());

                } catch (IOException e1) {
                    Log.d(TAG, "myConnectThread, run: Unable to close socket connection: " + e1.getMessage());
                }

            }

            try {

            } catch (NullPointerException e) {
                e.printStackTrace();
            }
        }

        // Closes the client socket and causes the thread to finish.
        public void cancel() {
            try {
                Log.d(TAG, "Cancel: Closing Client Socket");
                mmSocket.close();
            } catch (IOException e) {
                Log.d(TAG, "Cancel: Closing mySocket in ConnectThread Failed " + e.getMessage());
            }
        }
    }
}
