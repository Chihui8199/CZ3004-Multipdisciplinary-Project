package com.example.cx3004.customViews;

import android.content.Context;
import android.content.res.TypedArray;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.Nullable;

import com.example.cx3004.R;

public class SquareGridView extends View {
    public int gridSize; // size (height/width) of the grid
    private int dim; // number of boxes in the grid
    public int gridInterval; // size of grid boxes
    private Paint innerBorderPaint = new Paint();
    private Paint outerBorderPaint = new Paint();


    public SquareGridView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);

        TypedArray a = context.getTheme().obtainStyledAttributes(
                attrs,
                R.styleable.SquareGridView,
                0, 0);
        try {
            dim = a.getInt(R.styleable.SquareGridView_dim, 20);
            innerBorderPaint.setColor(a.getColor(R.styleable.SquareGridView_border_color, Color.BLACK));
            innerBorderPaint.setStrokeWidth(a.getInt(R.styleable.SquareGridView_inner_border_width, 2));
            outerBorderPaint.setColor(a.getColor(R.styleable.SquareGridView_border_color, Color.BLACK));
            outerBorderPaint.setStrokeWidth(a.getInt(R.styleable.SquareGridView_outer_border_width, 5));
        } finally {
            a.recycle();
        }
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        gridInterval = (int) Math.min(getHeight(), getWidth()) / dim;
        gridSize = gridInterval * dim;

        // resize grid view
        ViewGroup.LayoutParams params = getLayoutParams();
        params.height = gridSize;
        params.width = gridSize;
        setLayoutParams(params);
        setX(0);
        setY(0);

        // Draw grid outer border
        canvas.drawLines(new float[]{
                0, 0, gridSize, 0, // top border
                0, gridSize, gridSize, gridSize, // bottom border
                0, 0, 0, gridSize, // left border
                gridSize, 0, gridSize, gridSize, // right border
        },
                outerBorderPaint);

        // Draw vertical lines
        // for each grid box, draw the left border
        for (int i=1; i<dim; i++)
            canvas.drawLine(
                    i*gridInterval,
                    0,
                    i*gridInterval,
                    gridSize,
                    innerBorderPaint);

        // Draw vertical lines
        // for each grid box, draw the left border
        for (int i=1; i<dim; i++)
            canvas.drawLine(
                    0,
                    i*gridInterval,
                    gridSize,
                    i*gridInterval,
                    innerBorderPaint);
    }

}
