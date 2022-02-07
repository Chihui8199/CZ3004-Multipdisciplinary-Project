package com.example.cx3004;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.TextView;
import androidx.appcompat.widget.PopupMenu;
import androidx.fragment.app.Fragment;

public class MainActivity extends AppCompatActivity {

    // views
    TextView pageTitle;

    // fragments
    BluetoothSettingsFragment bluetoothSettingsFragment;
    ImageRecognitionFragment imageRecognitionFragment;
    FastestCarTaskFragment fastestCarTaskFragment;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // instantiate views
        pageTitle = (TextView) findViewById(R.id.page_title);

        // instantiate fragments
        bluetoothSettingsFragment = new BluetoothSettingsFragment();
        imageRecognitionFragment = new ImageRecognitionFragment();
        fastestCarTaskFragment = new FastestCarTaskFragment();

        // set page fragment
        setPage(imageRecognitionFragment, R.string.title_image_recognition);

    }

    public void setPage(Fragment fragment, int title){
        pageTitle.setText(title);
        getSupportFragmentManager()
                .beginTransaction()
                .replace(R.id.page_fragment, fragment)
                .commit();
    }

    public void showPopup(View v) {
        PopupMenu popup = new PopupMenu(this, v);
        popup.setOnMenuItemClickListener(
                new PopupMenu.OnMenuItemClickListener() {
                    @Override
                    public boolean onMenuItemClick(MenuItem item) {
                        switch (item.getItemId()) {
                            case R.id.bluetooth_settings_option:
                                setPage(bluetoothSettingsFragment, R.string.title_bluetooth_settings);
                                return true;
                            case R.id.image_recognition_option:
                                setPage(imageRecognitionFragment, R.string.title_image_recognition);
                                return true;
                            case R.id.fastest_car_task_option:
                                setPage(fastestCarTaskFragment, R.string.title_fastest_car_task);
                                return true;
                            default:
                                return false;
                        }
                    }
                }
        );
        MenuInflater inflater = popup.getMenuInflater();
        inflater.inflate(R.menu.nav_menu, popup.getMenu());
        popup.show();
    }


}