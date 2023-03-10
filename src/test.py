import plotly
import plotly.graph_objects as go
from model.triangulation import triangulate_angled, calc_best_right_angle
from config import storage
from model.snap import RawSnapData
from plot import plotly_circle, plotly_led_lines, plotly_intersection, plotly_pixel_data
from model.positions import pixel_positions, scale_pixels

if __name__ == "__main__":
    c1 = RawSnapData(storage / 'fiets_0_white')
    c2 = RawSnapData(storage / 'fiets_45')
    # c2 = RawSnapData(storage / 'fiets_90_white')
    c3 = RawSnapData(storage / 'fiets_240_white')
    # c3 = RawSnapData(storage / 'fiets_270_white_floor')

    """
    a = estimate_angle(c1, c2)
    b = estimate_angle(c2, c3)
    c = estimate_angle(c3, c1)
    c2.camera_pos.phi_estimate = a[0]
    c3.camera_pos.phi_estimate = c[0]
    """

    for i in range(10):
        angle_estimate = calc_best_right_angle(c1, c2, c3)
        c2.camera_pos.phi_estimate = angle_estimate[0]
        c3.camera_pos.phi_estimate = -angle_estimate[2]

        data = triangulate_angled(c1, c2, c3)
        pixel_positions.push(data)

        scale_pixels()

        c1.refit_camera()
        c2.refit_camera()
        c3.refit_camera()

        figure = go.Figure()
        plotly_circle(figure)

        plotly_pixel_data(figure, data)

        plotly_led_lines(figure, c1, 0, 'red')
        plotly_led_lines(figure, c2, c2.camera_pos.phi_estimate, 'green')
        plotly_led_lines(figure, c2, c3.camera_pos.phi_estimate, 'blue')

        print(f"{c1.camera_pos.phi_estimate} {c2.camera_pos.phi_estimate} {c3.camera_pos.phi_estimate}")

        figure.update_yaxes(scaleanchor="x", scaleratio=1)
        figure.update_layout(
            title={
                'text': f"Plot num {i}",
                'xanchor': 'center',
                'yanchor': 'top'})

        plotly.offline.plot(figure)
