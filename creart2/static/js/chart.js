const ventasChart = document.getElementById('ventasChart');

new Chart(ventasChart, {
    type: 'line',
    data: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        datasets: [{
            label: 'Ventas',
            data: [4500, 5200, 4800, 6100, 7200, 6800],
            borderColor: '#8b3a4b',
            fill: false
        }]
    }
});


const pedidosChart = document.getElementById('pedidosChart');

new Chart(pedidosChart, {
    type: 'bar',
    data: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        datasets: [{
            label: 'Pedidos',
            data: [45, 52, 48, 61, 72, 68],
            backgroundColor: '#8b3a4b'
        }]
    }
});