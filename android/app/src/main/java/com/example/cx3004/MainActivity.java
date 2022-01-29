package com.example.cx3004;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import androidx.appcompat.widget.Toolbar;

public class MainActivity extends AppCompatActivity {

    BluetoothSettingsFragment bluetoothSettingsFragment;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // set page fragment
        bluetoothSettingsFragment = new BluetoothSettingsFragment();
        getSupportFragmentManager()
                .beginTransaction()
                .replace(R.id.page_fragment, bluetoothSettingsFragment)
                .commit();
    }
}