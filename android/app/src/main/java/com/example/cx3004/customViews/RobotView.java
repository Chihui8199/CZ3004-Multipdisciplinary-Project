package com.example.cx3004.customViews;

import android.content.Context;
import android.content.res.TypedArray;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.util.AttributeSet;
import android.view.Gravity;
import android.view.ViewGroup;

import androidx.annotation.Nullable;

import com.example.cx3004.R;

public class RobotView extends androidx.appcompat.widget.AppCompatTextView  {
    private int gridInterval;
    public int x;
    public int y;
    public String direction;

    public RobotView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);

        setBackgroundResource(R.color.faint_orange);
        setGravity(Gravity.CENTER);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // draw triangle arrow
        int height = getHeight();
        int width = getWidth();
        int top = (int) 0.2 * height;
        int bottom = (int) 0.5 * height;
        int left = (int) 0.4 * width;
        int right = (int) 0.6 * width;
        Drawable triangleArrow = getResources().getDrawable(R.drawable.triangle_arrow_up, null);
        triangleArrow.setBounds(0, 0, getWidth(), getHeight());
        triangleArrow.draw(canvas);
    }

    public void setGridInterval(int gridInterval){
        this.gridInterval = gridInterval;

        // resize view
        ViewGroup.LayoutParams params = getLayoutParams();
        params.height = 4*gridInterval;
        params.width = 4*gridInterval;
        setLayoutParams(params);

        // set robot at 0, 0
        //setX(0);
        //setY(0);
        move(0, 3, "up");
    }

    public void move(int x, int y, String direction){
        // if coordinates are out of bounds, break out of function and not move the robot
        if (!checkBoundary(x, y)) return;

        // set direction
        switch (direction){
            case "left":
                setRotation(-90);
                this.direction = direction;
                break;
            case "right":
                setRotation(90);
                this.direction = direction;
                break;
            case "down":
                setRotation(180);
                this.direction = direction;
                break;
            case "up":
                this.direction = direction;
                break;
        }

        // set coordinates
        setX(x * gridInterval);
        setY((19-y) * gridInterval);
        this.x = x;
        this.y = y;

    }

    private boolean checkBoundary(int x, int y){
        return (0<= x & x <= 16) & (3 <= y & y <= 19);
    }
}
