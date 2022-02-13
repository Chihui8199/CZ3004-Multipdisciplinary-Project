package com.example.cx3004;

import android.Manifest;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.util.ArrayList;
import java.util.Set;
import java.util.UUID;

public class BluetoothPairingPage extends AppCompatActivity {
    private static final String TAG = "DebuggingBluetoothPairing";
    public static boolean active = false;
    private String connStatus;
    BluetoothAdapter mBluetoothAdapter;
    public ArrayList<BluetoothDevice> mDiscovBTDevices;
    public ArrayList<BluetoothDevice> mPairedBTDevices;
    public DeviceAdapterList mDiscovDeviceListAdapter;
    public DeviceAdapterList mPairedDeviceListAdapter;
    TextView connStatusTextView;
    ListView discovDevicesListView;
    ListView pairedDevicesListView;
    Button connectBtn;
    ProgressDialog clientConnectionDialog;
    ProgressDialog clientReconnectionDialog;

    SharedPreferences sharedPreferences;
    SharedPreferences.Editor editor;

    BluetoothConnectionService mBluetoothConnection;
    private static final UUID myUUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");
    public static BluetoothDevice mSelectedBTDevice;

    Handler reconnectionHandler = new Handler();
    Runnable clientReconnectionRunnable = new Runnable() {
        @Override
        public void run() {
            Log.d(TAG, "Reconnection: Starting reconnection runnable.");
            // if not connected to device, start a client thread
            if (!BluetoothConnectionService.BluetoothConnectionStatus){
                Log.d(TAG, "Reconnection: Device is still disconnected, starting client thread.");
                startBTConnection(mSelectedBTDevice, myUUID);
                // in 5 seconds, run this runnable again
                reconnectionHandler.postDelayed(clientReconnectionRunnable, 5000);
            } else Log.d(TAG, "Reconnection: Reconnection successful, stopping reconnection runnable loop.");
        }
    };


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.bluetooth_pairing_window);
        active = true;

        DisplayMetrics dm = new DisplayMetrics();
        getWindowManager().getDefaultDisplay().getMetrics(dm);

        // get bluetooth adapter
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();


        Switch bluetoothSwitch = (Switch) findViewById(R.id.bluetoothSwitch);
        if (mBluetoothAdapter != null){
            // if device has bluetooth capabilities, instantiate bluetooth connection service
            mBluetoothConnection = new BluetoothConnectionService(BluetoothPairingPage.this);

            // if bluetooth is enabled, set bluetooth switch to on
            if (mBluetoothAdapter.isEnabled()) {
                bluetoothSwitch.setChecked(true);
                bluetoothSwitch.setText("ON");
            }
        }

        // set adapters for list views
        discovDevicesListView = (ListView) findViewById(R.id.discovDevicesListView);
        pairedDevicesListView = (ListView) findViewById(R.id.pairedDevicesListView);
        mDiscovBTDevices = new ArrayList<>();
        mPairedBTDevices = new ArrayList<>();
        mDiscovDeviceListAdapter = new DeviceAdapterList(this, R.layout.device_adapter_view, mDiscovBTDevices);
        mPairedDeviceListAdapter = new DeviceAdapterList(this, R.layout.device_adapter_view, mPairedBTDevices);
        pairedDevicesListView.setAdapter(mPairedDeviceListAdapter);
        discovDevicesListView.setAdapter(mDiscovDeviceListAdapter);
        connectBtn = (Button) findViewById(R.id.connectBtn);

        // register receivers
        IntentFilter filter = new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED);
        registerReceiver(bondingBroadcastReceiver, filter);
        IntentFilter filter2 = new IntentFilter("ConnectionStatus");
        LocalBroadcastManager.getInstance(this).registerReceiver(btConnectionReceiver, filter2);
        IntentFilter BTIntent = new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED);
        registerReceiver(enableBTBroadcastReceiver, BTIntent);
        IntentFilter discoverIntent = new IntentFilter(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED);
        registerReceiver(discoverStatusBroadcastReceiver, discoverIntent);
        IntentFilter discoverDevicesIntent = new IntentFilter(BluetoothDevice.ACTION_FOUND);
        registerReceiver(discoveryBroadcastReceiver, discoverDevicesIntent);

        discovDevicesListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            // when discovered device is selected: initiate pairing with device
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                mBluetoothAdapter.cancelDiscovery(); // discovery takes alot of resources, cancel before attempting pairing
                String deviceName = mDiscovBTDevices.get(i).getName();
                String deviceAddress = mDiscovBTDevices.get(i).getAddress();
                Log.d(TAG, "onItemClick: A device is selected.");
                Log.d(TAG, "onItemClick: DEVICE NAME: " + deviceName);
                Log.d(TAG, "onItemClick: DEVICE ADDRESS: " + deviceAddress);
                if (Build.VERSION.SDK_INT > Build.VERSION_CODES.JELLY_BEAN_MR2) {
                    Log.d(TAG, "onItemClick: Initiating pairing with " + deviceName);
                    mDiscovBTDevices.get(i).createBond();
                }
            }
        });

        pairedDevicesListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            // when discovered device is selected: start an accept thread
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                mBluetoothAdapter.cancelDiscovery(); // discovery takes alot of resources, cancel before attempting connection
                String deviceName = mPairedBTDevices.get(i).getName();
                String deviceAddress = mPairedBTDevices.get(i).getAddress();
                Log.d(TAG, "onItemClick: A device is selected.");
                Log.d(TAG, "onItemClick: DEVICE NAME: " + deviceName);
                Log.d(TAG, "onItemClick: DEVICE ADDRESS: " + deviceAddress);
                mBluetoothConnection.startAcceptThread();
                mSelectedBTDevice = mPairedBTDevices.get(i);
            }
        });

        bluetoothSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean isChecked) {
                Log.d(TAG, "onChecked: Switch button toggled. Enabling/Disabling Bluetooth");
                // device does not have bluetooth capabilities, set bluetooth switch to off
                if (mBluetoothAdapter == null) {
                    Log.d(TAG, "enableDisableBT: Device does not support Bluetooth capabilities!");
                    Toast.makeText(BluetoothPairingPage.this, "Device Does Not Support Bluetooth capabilities!", Toast.LENGTH_SHORT).show();
                    compoundButton.setChecked(false);
                }

                // device has bluetooth capabilities, enable/disable bluetooth
                else {
                    // bluetooth switch has been turned on, enable bluetooth if it is not enabled
                    if (isChecked) {
                        compoundButton.setText("ON");
                        if (!mBluetoothAdapter.isEnabled()) {
                            Log.d(TAG, "enableDisableBT: enabling Bluetooth");
                            Log.d(TAG, "enableDisableBT: Making device discoverable for 15 minutes.");

                            // request permission to enable bluetooth and make device discoverable for 15 minutes
                            Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
                            discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 900);
                            startActivity(discoverableIntent);
                        }
                    }

                    // bluetooth switch has been turned off, disable bluetooth is it is enabled
                    else {
                        compoundButton.setText("OFF");
                        if (mBluetoothAdapter.isEnabled()) {
                            Log.d(TAG, "enableDisableBT: disabling Bluetooth");

                            // if bluetooth connection service is running, cancel all its threads and close its sockets
                            if (mBluetoothConnection != null) mBluetoothConnection.stop();

                            // disable bluetooth
                            mBluetoothAdapter.disable();

                            // clear listviews
                            mDiscovBTDevices.clear();
                            mPairedBTDevices.clear();
                            mDiscovDeviceListAdapter.notifyDataSetChanged();
                            mPairedDeviceListAdapter.notifyDataSetChanged();

                        }
                    }
                }
            }
        });

        connectBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (mSelectedBTDevice == null) {
                    Toast.makeText(BluetoothPairingPage.this, "Please Select a Device before connecting.", Toast.LENGTH_SHORT).show();
                } else {
                    startConnection();
                }
            }
        });

        // set connection status to disconnected
        connStatusTextView = (TextView) findViewById(R.id.connStatusTextView);
        connStatus = "Disconnected";
        sharedPreferences = getApplicationContext().getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
        if (sharedPreferences.contains("connStatus"))
            connStatus = sharedPreferences.getString("connStatus", "");
        connStatusTextView.setText(connStatus);

        ImageButton backBtn = findViewById(R.id.backBtn);
        backBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editor = sharedPreferences.edit();
                editor.putString("connStatus", connStatusTextView.getText().toString());
                editor.commit();
                finish();
            }
        });

        // set connection dialog
        clientConnectionDialog = new ProgressDialog(BluetoothPairingPage.this);
        clientConnectionDialog.setTitle("Connecting Bluetooth");
        clientConnectionDialog.setMessage("Please Wait...");
        clientConnectionDialog.setIndeterminate(true);

        // set reconnection dialog
        clientReconnectionDialog = new ProgressDialog(BluetoothPairingPage.this);
        clientReconnectionDialog.setTitle("Reconnecting");
        clientReconnectionDialog.setMessage("Waiting for other device to reconnect...");
        clientReconnectionDialog.setCancelable(true);
        clientReconnectionDialog.setCanceledOnTouchOutside(true);
        clientReconnectionDialog.setOnCancelListener(new DialogInterface.OnCancelListener() {
            @Override
            public void onCancel(DialogInterface dialogInterface) {
                // stop client reconnection loop
                reconnectionHandler.removeCallbacks(clientReconnectionRunnable);
                // stop all threads in bluetooth connection service
                mBluetoothConnection.stop();
            }
        });
    }

    public void scanForDevices(View view) {
        Log.d(TAG, "scanForDevices(): Scanning for unpaired devices.");

        // reset discovered devices and paired devices lists
        mDiscovBTDevices.clear();
        mPairedBTDevices.clear();

        // device has bluetooth capabilities
        if (mBluetoothAdapter != null) {
            // bluetooth has not been enabled
            if (!mBluetoothAdapter.isEnabled()) Toast.makeText(BluetoothPairingPage.this, "Please turn on Bluetooth first!", Toast.LENGTH_SHORT).show();
            // bluetooth is enabled
            else {
                // if bluetooth adapter is already discovering, restart discovery
                if (mBluetoothAdapter.isDiscovering()) {
                    mBluetoothAdapter.cancelDiscovery();
                    Log.d(TAG, "scanForDevices(): Cancelling Discovery.");
                    checkBTPermissions();
                    mBluetoothAdapter.startDiscovery();
                    Log.d(TAG, "scanForDevices(): Starting Discovery.");
                }
                // if bluetooth adapter is not discovering, start discovery
                else {
                    checkBTPermissions();
                    mBluetoothAdapter.startDiscovery();
                    Log.d(TAG, "scanForDevices(): Starting Discovery.");
                }
            }
            // list paried devices
            Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
            Log.d(TAG, "toggleButton: Number of paired devices found: " + pairedDevices.size());
            for (BluetoothDevice d : pairedDevices) {
                Log.d(TAG, "Paired Devices: " + d.getName() + " : " + d.getAddress());
                mPairedBTDevices.add(d);
            }
        }

        // device does not have bluetooth capabilities
        else Toast.makeText(BluetoothPairingPage.this, "Device Does Not Support Bluetooth capabilities!", Toast.LENGTH_SHORT).show();

        // update paired devices list view
        mPairedDeviceListAdapter.notifyDataSetChanged();
    }

    private void checkBTPermissions() {
        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.LOLLIPOP) {
            int permissionCheck = this.checkSelfPermission("Manifest.permission.ACCESS_FINE_LOCATION");
            permissionCheck += this.checkSelfPermission("Manifest.permission.ACCESS_COARSE_LOCATION");
            if (permissionCheck != 0) {
                this.requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, 1001);
            }
        } else {
            Log.d(TAG, "checkBTPermissions: No need to check permissions. SDK version < LOLLIPOP.");

        }
    }

    // BroadcastReceiver 1: BroadcastReceiver for ACTION_STATE_CHANGED (ENABLE/DISABLE BLUETOOTH)
    private final BroadcastReceiver enableBTBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (action.equals(mBluetoothAdapter.ACTION_STATE_CHANGED)) {
                final int state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR);
                switch (state) {
                    case BluetoothAdapter.STATE_OFF:
                        Log.d(TAG, "mBroadcastReceiver1: STATE OFF");
                        Toast.makeText(BluetoothPairingPage.this, "Bluetooth disabled.", Toast.LENGTH_SHORT).show();
                        break;
                    case BluetoothAdapter.STATE_TURNING_OFF:
                        Log.d(TAG, "mBroadcastReceiver1: STATE TURNING OFF");
                        break;
                    case BluetoothAdapter.STATE_ON:
                        Log.d(TAG, "mBroadcastReceiver1: STATE ON");
                        Toast.makeText(BluetoothPairingPage.this, "Bluetooth enabled.", Toast.LENGTH_SHORT).show();
                        break;
                    case BluetoothAdapter.STATE_TURNING_ON:
                        Log.d(TAG, "mBroadcastReceiver1: STATE TURNING ON");
                        break;
                }
            }
        }
    };

    // Broadcast Receiver 2: BroadcastReceiver for ACTION_SCAN_MODE_CHANGED (discovering status)
    private final BroadcastReceiver discoverStatusBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (action.equals(mBluetoothAdapter.ACTION_SCAN_MODE_CHANGED)) {
                final int mode = intent.getIntExtra(BluetoothAdapter.EXTRA_SCAN_MODE, BluetoothAdapter.ERROR);
                switch (mode) {
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE_DISCOVERABLE:
                        Log.d(TAG, "mBroadcastReceiver2: Discoverability Enabled.");
                        break;
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE:
                        Log.d(TAG, "mBroadcastReceiver2: Discoverability Disabled. Able to receive connections.");
                        break;
                    case BluetoothAdapter.SCAN_MODE_NONE:
                        Log.d(TAG, "mBroadcastReceiver2: Discoverability Disabled. Not able to receive connections.");
                        break;
                    case BluetoothAdapter.STATE_CONNECTING:
                        Log.d(TAG, "mBroadcastReceiver2: Connecting...");
                        break;
                    case BluetoothAdapter.STATE_CONNECTED:
                        Log.d(TAG, "mBroadcastReceiver2: Connected.");
                        break;
                }
            }
        }
    };

    // Broadcast Receiver 3: BroadcastReceiver for ACTION_FOUND (Get Discovered Devices Info)
    private BroadcastReceiver discoveryBroadcastReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();
            Log.d(TAG, "onReceive: SEARCHING.");
            if (action.equals(BluetoothDevice.ACTION_FOUND)) {
                // add discovered device to discovered device list view
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                mDiscovBTDevices.add(device);
                mDiscovDeviceListAdapter.notifyDataSetChanged();
                Log.d(TAG, "onReceive: " + device.getName() + " : " + device.getAddress());
            }
        }
    };

    // Broadcast Receiver 4: BroadcastReceiver for ACTION_BOND_STATE_CHANGED (Pairing Devices)
    private BroadcastReceiver bondingBroadcastReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();
            if (action.equals(BluetoothDevice.ACTION_BOND_STATE_CHANGED)) {
                BluetoothDevice mDevice = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                switch (mDevice.getBondState()){
                    case BluetoothDevice.BOND_BONDED:
                        Log.d(TAG, "BOND_BONDED.");
                        Toast.makeText(BluetoothPairingPage.this, "Successfully paired with " + mDevice.getName(), Toast.LENGTH_SHORT).show();
                        mSelectedBTDevice = mDevice;
                        // add paired device to paired device list view
                        mPairedBTDevices.add(mDevice);
                        mPairedDeviceListAdapter.notifyDataSetChanged();
                        break;
                    case BluetoothDevice.BOND_BONDING:
                        Log.d(TAG, "BOND_BONDING.");
                        break;
                    case BluetoothDevice.BOND_NONE:
                        Log.d(TAG, "BOND_NONE.");
                        String deviceName = mDevice.getName();
                        deviceName = (deviceName == null) ? mDevice.getAddress() : deviceName;
                        Toast.makeText(BluetoothPairingPage.this, String.format("Failed to pair with %s. Please try again!", deviceName), Toast.LENGTH_SHORT).show();
                        break;
                }
            }
        }
    };

    // Broadcast Receiver 5: Local BroadcastReceiver for Bluetooth Connection Status
    private BroadcastReceiver btConnectionReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            BluetoothDevice mDevice = intent.getParcelableExtra("Device");
            String status = intent.getStringExtra("Status");
            sharedPreferences = getApplicationContext().getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
            editor = sharedPreferences.edit();
            if (status.equals("connected")) {
                // if connection/reconnection dialog is showing, dismiss it
                if (clientConnectionDialog.isShowing()) clientConnectionDialog.dismiss();
                if (clientReconnectionDialog.isShowing()) clientReconnectionDialog.dismiss();

                Log.d(TAG, "mBroadcastReceiver5: Device now connected to " + mDevice.getName());
                Toast.makeText(BluetoothPairingPage.this, "Device now connected to " + mDevice.getName(), Toast.LENGTH_SHORT).show();
                editor.putString("connStatus", "Connected to " + mDevice.getName());
                connStatusTextView.setText("Connected to " + mDevice.getName());
            } else if (status.equals("disconnected")) {
                Log.d(TAG, "mBroadcastReceiver5: Disconnected from " + mDevice.getName());
                Toast.makeText(BluetoothPairingPage.this, "Disconnected from " + mDevice.getName(), Toast.LENGTH_SHORT).show();
                sharedPreferences = getApplicationContext().getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
                editor = sharedPreferences.edit();
                editor.putString("connStatus", "Disconnected");
                TextView connStatusTextView = findViewById(R.id.connStatusTextView);
                connStatusTextView.setText("Disconnected");
                editor.commit();

                // only run reconnection if bluetooth is enabled
                Log.d(TAG, "BluetoothPairingPage activity " + ((BluetoothPairingPage.active)? "is" : "is not") + " active.");
                if (mBluetoothAdapter.isEnabled()){
                    Log.d(TAG, "mBroadcastReceiver5: Attempting reconnection.");
                    // show reconnection dialog
                    clientReconnectionDialog.show();
                    // start server thread
                    Log.d(TAG, "Reconnection: Starting server thread.");
                    mBluetoothConnection.startAcceptThread();

                    // start client thread
                    // while the device remains disconnected, check every 5 seconds if connection was successful.
                    // if no, start a new client thread.
                    //(code is commented out for amd. amd reconnection must be initiated from the amd itself, only server thread should be running)
                    //clientReconnectionRunnable.run();
                }

            }
            editor.commit();
        }
    };

    // start connection through client thread
    public void startConnection() {
        clientConnectionDialog.show(); // show connection dialog
        startBTConnection(mSelectedBTDevice, myUUID); // start client thread
    }

    // start client thread
    public void startBTConnection(BluetoothDevice device, UUID uuid) {
        Log.d(TAG, "startBTConnection: Initializing RFCOM Bluetooth Connection");
        mBluetoothConnection.startClientThread(device, uuid);
    }

    @Override
    protected void onDestroy() {
        active = false;
        Log.d(TAG, "onDestroy: called");
        super.onDestroy();
        try {
            unregisterReceiver(enableBTBroadcastReceiver);
            unregisterReceiver(discoveryBroadcastReceiver);
            unregisterReceiver(bondingBroadcastReceiver);
            LocalBroadcastManager.getInstance(this).unregisterReceiver(btConnectionReceiver);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onResume() {
        Log.d(TAG, "onResume: called");
        super.onResume();
        active = true;
    }

    @Override
    protected void onPause() {
        Log.d(TAG, "onPause: called");
        active = false;
        super.onPause();
    }

    @Override
    public void finish() {
        Intent data = new Intent();
        data.putExtra("mBTDevice", mSelectedBTDevice);
        data.putExtra("myUUID", myUUID);
        setResult(RESULT_OK, data);
        super.finish();
    }
}
