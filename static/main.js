var chartDiv = document.getElementById("chart-div");
var toggleButton = document.getElementById("chart-toggle");

var chartHidden = false;

function toggleChartVisibility() {
    chartHidden = !chartHidden;
    toggleButton.textContent = (chartHidden ? "Pokaż" : "Ukryj") + " wykres";
    toggleButton.classList.toggle("rotated");
    chartDiv.hidden = chartHidden;
}

toggleButton.onclick = function () {
    toggleChartVisibility();
};

const ctx = document.getElementById("temperature-chart");
const t_data = window.chartData;

const data = {
    datasets: [
        {
            label: "Temperatura",
            data: t_data,
            fill: false,
            borderColor: "#841d28",
            cubicInterpolationMode: "default",
            tension: 0.4,
        },
    ],
};

new Chart(ctx, {
    type: "line",
    data: data,
    options: {
        locale: "pl-PL",
        scales: {
            x: {
                type: "time",
                time: {
                    displayFormats: {
                        hour: "HH:mm",
                    },
                },
                unit: "hour",
            },
            y: {
                ticks: {
                    callback: function (value, _, _) {
                        return value.toFixed(1) + "°C";
                    },
                },
            },
        },
        plugins: {
            legend: {
                display: false,
            },
        },
        responsive: true,
    },
});
