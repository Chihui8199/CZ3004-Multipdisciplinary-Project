package com.example.cx3004;

import android.Manifest;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.bluetooth.BluetoothAdapter;
import android.view.View;
import android.widget.Button;
import android.widget.ListView;
import android.widget.Toast;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;

import java.util.ArrayList;


public class BluetoothActivity extends AppCompatActivity {
    // Tag BTCheck for logging errors
    private static final String TAG = "BTCheck";
    BluetoothAdapter myBluetoothAdapter;
    //Array List to hold bluetooth devices discovered
    public ArrayList<BluetoothDevice> myBTDevicesArrayList = new ArrayList<>();
    public DeviceAdapterList myFoundAdapterListItem;

    ListView lvNewDevices;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth_settings);

        myBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        // On/Off Button
        Button btnOnOff = findViewById(R.id.bluetoothSwitch);
        ListView lvNewDevices = findViewById(R.id.lvNewDevices);

        // Register Enable/Disable Bluetooth Broadcast Receiver
        IntentFilter BTIntent = new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED);
        registerReceiver(enableBTBroadcastReceiver, BTIntent);

        // Register Discoverability States Broadcast Receiver
        IntentFilter intentFilter = new IntentFilter(myBluetoothAdapter.ACTION_SCAN_MODE_CHANGED);
        registerReceiver(discoverabilityStatesBroadcastReceiver, intentFilter);

        // Register Discovered Device Broadcast Receiver
        IntentFilter discoverDevicesIntent = new IntentFilter(BluetoothDevice.ACTION_FOUND);
        registerReceiver(discoverDevicesBroadcastReceiver, discoverDevicesIntent);


        btnOnOff.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d(TAG, "onClick: Enabling/Disabling Bluetooth");
                enableBT();
            }
        });
    }

    // Enable Bluetooth
    public void enableBT() {
        // Device does not have Bluetooth
        if (myBluetoothAdapter == null) {
            Toast.makeText(BluetoothActivity.this, "Device Does Not Support Bluetooth.",
                    Toast.LENGTH_LONG).show();
            Log.d(TAG, "enableDisableBT: Does not have BT capabilities.");
        }
        // Device's Bluetooth is disabled
        if (!myBluetoothAdapter.isEnabled()) {
            Log.d(TAG, "enableDisableBT: disabling BT.");
            Intent enableBTIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivity(enableBTIntent);
        }
        // Device's Bluetooth is enabled
        if (myBluetoothAdapter.isEnabled()) {
            Log.d(TAG, "enableDisableBT: enabling BT.");
            discoverabilityON();
        }

    }

    // Turn On Discoverability
    private void discoverabilityON() {
        Log.d(TAG, "enableDisableBT: enabling this device to be discovered.");
        Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
        discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 900);
        startActivity(discoverableIntent);
    }

    private void startSearch() {
        Log.d(TAG, "btnDiscover: Looking for unpaired devices.");

        // Discover devices
        if (myBluetoothAdapter.isDiscovering()) {
            myBluetoothAdapter.cancelDiscovery();
            Log.d(TAG, "BTDiscovery: canceling discovery");

            // Check Bluetooth Permission in Manifest
            checkBTPermission();

            myBluetoothAdapter.startDiscovery();
            Log.d(TAG, "BTDiscovery: enable discovery");

        }
        if (!myBluetoothAdapter.isDiscovering()) {

            // Check Bluetooth Permission in Manifest
            checkBTPermission();
            myBluetoothAdapter.startDiscovery();
            Log.d(TAG, "BTDiscovery: enable discovery");
        }
    }

    /**
     * This method is required for all devices running API23+
     * Android must programmatically check the permissions for bluetooth. Putting the proper permissions
     * in the manifest is not enough.
     */
    @RequiresApi(api = Build.VERSION_CODES.M)
    private void checkBTPermission() {
        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP){
            int permissionCheck = 0;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                permissionCheck = this.checkSelfPermission("Manifest.permission.ACCESS_COARSE_LOCATION")
                        + this.checkSelfPermission("Manifest.permission.ACCESS_FINE_LOCATION");
            }
            if(permissionCheck != 0){
                this.requestPermissions(new String[] {Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION},
                        1001);
            }
        }
    }

    // Create a BroadcastReceiver for ACTION_FOUND (EnableBT)
    private final BroadcastReceiver enableBTBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (action.equals(myBluetoothAdapter.ACTION_STATE_CHANGED)) {
                final int state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, myBluetoothAdapter.ERROR);

                switch (state) {
                    // Bluetooth STATE OFF
                    case BluetoothAdapter.STATE_OFF:
                        Log.d(TAG, "OnReceiver: STATE OFF");
                        break;
                    // Bluetooth STATE TURNING OFF
                    case BluetoothAdapter.STATE_TURNING_OFF:
                        Log.d(TAG, "OnReceiver: STATE TURNING OFF");
                        break;
                    // Bluetooth STATE ON
                    case BluetoothAdapter.STATE_ON:
                        Log.d(TAG, "OnReceiver: STATE ON");
                        // Turn on discoverability
                        discoverabilityON();
                        break;
                    // Bluetooth STATE TURNING ON
                    case BluetoothAdapter.STATE_TURNING_ON:
                        Log.d(TAG, "OnReceiver: STATE TURNING ON");
                        break;
                }
            }
        }
    };

    // Create a BroadcastReceiver for changes made to bluetooth states
    private final BroadcastReceiver discoverabilityStatesBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();
            if (action.equals(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED)) {
                int mode = intent.getIntExtra(BluetoothAdapter.EXTRA_SCAN_MODE, BluetoothAdapter.ERROR);

                switch (mode) {
                    // Device is on discoverable mode
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE_DISCOVERABLE:
                        Log.d(TAG, "OnReceiver: DISCOVERABILITY ENABLED");
                        // Discover devices
                        startSearch();
//                        // Start BluetoothConnectionService to listen for connection
//                        connectIntent = new Intent(getContext(), BluetoothComms.class);
//                        connectIntent.putExtra("serviceType", "listen");
//                        getActivity().startService(connectIntent);
//
//                        // Check Paired Devices list
//                        checkPairedDevice();
                        break;
                    // Device not on discoverable mode
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE:
                        Log.d(TAG, "OnReceiver: DISCOVERABILITY DISABLED, ABLE TO RECEIVE CONNECTION");
                        break;
                    // Device not in valid scan mode
                    case BluetoothAdapter.SCAN_MODE_NONE:
                        Log.d(TAG, "OnReceiver: DISCOVERABILITY DISABLED, NOT ABLE TO RECEIVE CONNECTION");
                        break;
                    // Bluetooth STATE CONNECTING
                    case BluetoothAdapter.STATE_CONNECTING:
                        Log.d(TAG, "OnReceiver: CONNECTING");
                        break;
                    // Bluetooth State CONNECTED
                    case BluetoothAdapter.STATE_CONNECTED:
                        Log.d(TAG, "OnReceiver: CONNECTED");
                        break;
                }
            }
        }
    };

    // Create a BroadcastReceiver for ACTION_FOUND (Get Discovered Devices Info)
    private final BroadcastReceiver discoverDevicesBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();
            Log.d(TAG, "SEARCHING!");

            if (action.equals(BluetoothDevice.ACTION_FOUND)) {
                BluetoothDevice device = intent.getParcelableExtra (BluetoothDevice.EXTRA_DEVICE);
                myBTDevicesArrayList.add(device);
                Log.d(TAG, "onReceive: " + device.getName() + ": " + device.getAddress());
                myFoundAdapterListItem = new DeviceAdapterList(context, R.layout.device_adapter_view, myBTDevicesArrayList);
                lvNewDevices.setAdapter(myFoundAdapterListItem);
            }
        }
    };

    // Unregister receivers
    @Override
    public void onDestroy() {
        Log.d(TAG, "ConnectActivity: onDestroyed: destroyed");
        super.onDestroy();
        unregisterReceiver(enableBTBroadcastReceiver);
        unregisterReceiver(discoverabilityStatesBroadcastReceiver);
    }

}
