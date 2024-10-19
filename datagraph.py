import flet as ft
import matplotlib.pyplot as plt
from io import BytesIO
import base64
def plot_graph(data: dict):
    # Sort data by date to ensure the x-axis is in the correct order
    sorted_data = sorted(data.items())
    dates = [item[0] for item in sorted_data]
    times = [item[1] for item in sorted_data]

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(dates, times, marker='o')

    # Set labels
    ax.set_xlabel("Date")
    ax.set_ylabel("Times")
    ax.set_title("Times vs. Date")

    # Ensure the y-axis starts from 0 and increases upwards
    ax.set_ylim(bottom=0)

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Convert the plot to a base64 string for Flet Image
    img_data = buffer.getvalue()
    plt.close(fig)  # Close the figure after saving to free resources

    return img_data


def main(page: ft.Page):
    data = {
        "2023-08-01": 3,
        "2023-08-02": 5,
        "2023-08-03": 4,
        "2023-08-04": 2,
        "2023-08-05": 6
    }

    img_data = plot_graph(data)

    # Display the image on Flet
    image = ft.Image(src_base64=base64.b64encode(img_data).decode("utf-8"), width=600, height=400)
    page.add(image)

    page.update()


ft.app(target=main)
