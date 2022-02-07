package com.example.cx3004;

import android.Manifest;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothHeadset;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.bluetooth.BluetoothAdapter;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.Toast;

import androidx.annotation.RequiresApi;
import androidx.fragment.app.Fragment;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Set;
import java.util.UUID;


public class BluetoothSettingsFragment extends Fragment {

    private static final String TAG = "BTCheck";
    private static final UUID myUUID = UUID.fromString("9ac5e66c-882b-11ec-a8a3-0242ac120002");

    //Array List to hold bluetooth devices discovered
    ArrayList<BluetoothDevice> myBTDevicesArrayList = new ArrayList<>();
    DeviceAdapterList myFoundAdapterListItem;
    //Array List to hold bluetooth devices paired
    ArrayList<BluetoothDevice> myBTPairedDevicesArrayList = new ArrayList<>();
    DeviceAdapterList myPairedDeviceAdapterListItem;

    static BluetoothDevice myBTDevice;
    BluetoothDevice myBTConnectionDevice;
    BluetoothAdapter myBluetoothAdapter;
    Intent connectIntent;

    Button btnOnOff;
    Button bluetoothConnect;
    ListView lvFoundDevices;
    ListView lvPairedDevices;
    ProgressDialog myProgressDialog;
    //Button btnStartConnection;
    ImageButton btnSend;
    EditText message_list;
    StringBuilder incomingMsg;
    EditText sendMessage;
    View view;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        view = inflater.inflate(R.layout.fragment_bluetooth_settings, container, false);
        return view;
    }


    public void onViewCreated(View view, Bundle savedInstanceState) {

        myBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        // Getting Ui objects
        btnOnOff = getActivity().findViewById(R.id.bluetooth_button);

        lvFoundDevices = getActivity().findViewById(R.id.lvNewDevices);
        lvPairedDevices = getActivity().findViewById(R.id.lvPairedDevices);
        message_list = getActivity().findViewById(R.id.message_list);
        sendMessage = getActivity().findViewById(R.id.sender_input_text);
        btnSend = getActivity().findViewById(R.id.sendBtn);
        incomingMsg = new StringBuilder();
        myBTDevice = null;
        // btnSend.setEnabled(false);

        //Register BroadcastReceiver for ACTION_FOUND (ENABLE/DISABLE BLUETOOTH)
        IntentFilter BTIntent = new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED);
        getActivity().registerReceiver(enableBTBroadcastReceiver, BTIntent);

        // Register Broadcast Receiver for changes made to bluetooth states (Discoverability mode on/off or expire)
        IntentFilter intentFilter = new IntentFilter(myBluetoothAdapter.ACTION_SCAN_MODE_CHANGED);
        getActivity().registerReceiver(discoverStatusBroadcastReceiver, intentFilter);

        // Register Broadcast Receiver for Discovered Device
        IntentFilter discoverDevicesIntent = new IntentFilter(BluetoothDevice.ACTION_FOUND);
        getActivity().registerReceiver(discoveringDevicesBroadcastReceiver, discoverDevicesIntent);

        // Register broadcast when bond state changed (E.g. PAIRING)
        IntentFilter bondFilter = new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED);
        getActivity().registerReceiver(bondingBroadcastReceiver, bondFilter);

        btnOnOff.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d(TAG, "onClick: Enabling/Disabling Bluetooth");
                enableBT();
            }
        });

        // onClick Listener for Search Device List to pair with a device
        lvFoundDevices.setOnItemClickListener(
                new AdapterView.OnItemClickListener() {
                    @Override
                    public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                        // Cancel Device Search Discovery
                        myBluetoothAdapter.cancelDiscovery();
                        Log.d(TAG, "onItemClick: Item Selected");
                        String deviceName = myBTDevicesArrayList.get(i).getName();
                        String deviceAddress = myBTDevicesArrayList.get(i).getAddress();
                        // Deselect Paired Device List
                        lvPairedDevices.setAdapter(myPairedDeviceAdapterListItem);
                        Log.d(TAG, "onItemClick: DeviceName = " + deviceName);
                        Log.d(TAG, "onItemClick: DeviceAddress = " + deviceAddress);
                        // Create bond if > JELLYBEAN
                        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.JELLY_BEAN_MR2) {
                            Log.d(TAG, "Trying to pair with: " + deviceName);
                            // Create bond with selected device
                            myBTDevicesArrayList.get(i).createBond();

                            // Assign selected device info to myBTDevice
                            myBTDevice = myBTDevicesArrayList.get(i);
                        }
                    }
                }
        );

        // onClick Listener for Paired Device List and added paired device to discover items
        lvPairedDevices.setOnItemClickListener(
                new AdapterView.OnItemClickListener() {
                    @Override
                    public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                        // Cancel device search discovery
                        myBluetoothAdapter.cancelDiscovery();
                        myBTDevice = myBTPairedDevicesArrayList.get(i);
                        //Deselect Search Device List
                        lvFoundDevices.setAdapter(myFoundAdapterListItem);
                        Log.d(TAG, "onItemClick: Paired Device = " + myBTPairedDevicesArrayList.get(i).getName());
                        Log.d(TAG, "onItemClick: DeviceAddress = " + myBTPairedDevicesArrayList.get(i).getAddress());
                        if (myBTDevice == null) {
                            Toast.makeText(getContext(), "Not Connected! Pairing Unsuccessful. Please Search/Select a Device.",
                                    Toast.LENGTH_LONG).show();
                        } else {
                            //TODO send is only enabled onced paired need to check for connection status too
                            //TODO grey out button when disabled
                            btnSend.setEnabled(true);
                        }
                    }
                }
        );
    }

    // Enable Bluetooth
    public void enableBT() {
        // Device does not have Bluetooth
        if (myBluetoothAdapter == null) {
            Toast.makeText(getContext(), "Device Does Not Support Bluetooth.",
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
            // Turns on Discoverability
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

    // Process of searching for unpaired devices
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

    // Check for paired devices
    public void checkPairedDevice() {
        Set<BluetoothDevice> pairedDevices = myBluetoothAdapter.getBondedDevices();
        myBTPairedDevicesArrayList.clear();
        if (pairedDevices.size() > 0) {
            for (BluetoothDevice device : pairedDevices) {
                Log.d(TAG, "PAIRED DEVICES: " + device.getName() + "," + device.getAddress());
                myBTPairedDevicesArrayList.add(device);
            }
            myPairedDeviceAdapterListItem = new DeviceAdapterList(getContext(), R.layout.device_adapter_view, myBTPairedDevicesArrayList);
            lvPairedDevices.setAdapter(myPairedDeviceAdapterListItem);

        } else {
            Log.d(TAG, "NO PAIRED DEVICE!!");
        }
    }

    /**
     * This method is required for all devices running API23+
     * Android must programmatically check the permissions for bluetooth. Putting the proper permissions
     * in the manifest is not enough.
     */
    @RequiresApi(api = Build.VERSION_CODES.M)
    private void checkBTPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            int permissionCheck = 0;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                permissionCheck = getActivity().checkSelfPermission("Manifest.permission.ACCESS_COARSE_LOCATION")
                        + getActivity().checkSelfPermission("Manifest.permission.ACCESS_FINE_LOCATION");
            }
            if (permissionCheck != 0) {
                this.requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION},
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
    private final BroadcastReceiver discoverStatusBroadcastReceiver = new BroadcastReceiver() {
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
                        // Check Paired Devices list
                        checkPairedDevice();
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
    private final BroadcastReceiver discoveringDevicesBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();
            Log.d(TAG, "SEARCHING!");
            if (action.equals(BluetoothDevice.ACTION_FOUND)) {
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                myBTDevicesArrayList.add(device);
                Log.d(TAG, "onReceive: " + device.getName() + ": " + device.getAddress());
                myFoundAdapterListItem = new DeviceAdapterList(context, R.layout.device_adapter_view, myBTDevicesArrayList);
                lvFoundDevices.setAdapter(myFoundAdapterListItem);
            }
        }
    };

    // Create a BroadcastReceiver for ACTION_FOUND (Pairing Devices)
    private final BroadcastReceiver bondingBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {

            final String action = intent.getAction();

            if (action.equals(BluetoothDevice.ACTION_BOND_STATE_CHANGED)) {

                // Bonding device
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                // case 1: Device already bonded
                if (device.getBondState() == BluetoothDevice.BOND_BONDED) {
                    Log.d(TAG, "BoundReceiver: Bond Bonded with: " + device.getName());
                    //Deprecated
                    myProgressDialog.dismiss();
                    Toast.makeText(getContext(), "Paired Successfully With: " + device.getName(),
                            Toast.LENGTH_LONG).show();
                    // Assign global bluetooth device to the device that it has paired with
                    myBTDevice = device;
                    checkPairedDevice();
                    //listview
                    lvFoundDevices.setAdapter(myFoundAdapterListItem);
                }
                // case 2: Device is bonded with another device
                if (device.getBondState() == BluetoothDevice.BOND_BONDING) {
                    Log.d(TAG, "BoundReceiver: Pairing With Another Device");
                    myProgressDialog = ProgressDialog.show(getContext(), "Pairing With Device", "Please Wait...", true);
                }
                // case 3:  Break bond
                if (device.getBondState() == BluetoothDevice.BOND_NONE) {
                    Log.d(TAG, "BoundReceiver: Breaking Bond");
                    myProgressDialog.dismiss();
                    AlertDialog alertDialog = new AlertDialog.Builder(getContext()).create();
                    alertDialog.setTitle("Pairing Status");
                    alertDialog.setMessage("Pairing Unsuccessful!");
                    alertDialog.setButton(AlertDialog.BUTTON_NEUTRAL, "OK",
                            new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface dialog, int which) {
                                    dialog.dismiss();
                                }
                            });
                    alertDialog.show();
                    // Reset variable
                    myBTDevice = null;
                }

            }
        }
    };

    //     Unregister receivers
    @Override
    public void onDestroy() {
        Log.d(TAG, "ConnectActivity: onDestroyed: destroyed");
        super.onDestroy();
        try {
            getActivity().unregisterReceiver(enableBTBroadcastReceiver);
            getActivity().unregisterReceiver(discoverStatusBroadcastReceiver);
            getActivity().unregisterReceiver(discoveringDevicesBroadcastReceiver);
            getActivity().unregisterReceiver(bondingBroadcastReceiver);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }
}
