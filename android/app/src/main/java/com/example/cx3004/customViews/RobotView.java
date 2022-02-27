package com.example.cx3004.customViews;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.drawable.Drawable;
import android.util.AttributeSet;
import android.view.Gravity;
import android.view.ViewGroup;

import androidx.annotation.Nullable;

import com.example.cx3004.R;

public class RobotView extends androidx.appcompat.widget.AppCompatTextView {
    private int gridInterval;
    // coordinates are measured from center of the robot
    public double gridX;
    public double gridY;
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

    public void setGridInterval(int gridInterval) {
        this.gridInterval = gridInterval;

        // resize view
        ViewGroup.LayoutParams params = getLayoutParams();
        params.height = 4 * gridInterval;
        params.width = 4 * gridInterval;
        setLayoutParams(params);

        // set robot at 0, 0
        //setX(0);
        //setY(0);
        move(1.5, 1.5, "up");
    }


    public void move(double x, double y, String direction){
        // set direction
        switch (direction) {
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
                setRotation(0);
                this.direction = direction;
                break;
        }

        // set coordinates
        setX((float) ((x - 1.5) * gridInterval));
        setY((float) ((19 - y - 1.5) * gridInterval));
        this.gridX = x;
        this.gridY = y;
    }

    public boolean checkBoundary(double x, double y){
        return (1.5<= x & x <= 17.5) & (1.5 <= y & y <= 17.5);
    }

    public double getGridX(){
        return gridX;
    }

    public double getGridY(){
        return gridY;
    }

    public String getRobotDirection(){
        return direction;
    }
}
