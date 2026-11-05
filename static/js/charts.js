document.addEventListener("DOMContentLoaded", function() {

    // Configura e processa os dados temporais para montar gráficos interativos por Semana, Mês ou Ano
    function setupClientSideTemporalChart(canvasId, selectId, rawDataId, datasetType) {
        const canvas = document.getElementById(canvasId);
        const select = document.getElementById(selectId);
        const dataElem = document.getElementById(rawDataId);

        if (!canvas || !dataElem) return;

        const rawItems = JSON.parse(dataElem.textContent || '[]');

        // Agrupa os itens brutos do JSON nas faixas temporais correspondentes (Semana, Mês e Ano)
        function processData() {
            const now = new Date();

            const labelsWeek = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
            const labelsMonth = ["Dias 1-7", "Dias 7-14", "Dias 14-21", "Dias 21-31"];
            const labelsYear = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

            let weekAct = [0,0,0,0,0,0,0], weekInact = [0,0,0,0,0,0,0], weekTot = [0,0,0,0,0,0,0];
            let monthAct = [0,0,0,0], monthInact = [0,0,0,0], monthTot = [0,0,0,0];
            let yearAct = new Array(12).fill(0), yearInact = new Array(12).fill(0), yearTot = new Array(12).fill(0);

            // Converte o índice padrão de dias do JS para o formato baseado em segunda-feira (0 = Segunda ... 6 = Domingo)
            function getMondayBasedDay(d) {
                let day = d.getDay();
                return day === 0 ? 6 : day - 1;
            }

            // Valida se uma determinada data cai dentro da semana atual
            function isCurrentWeek(d) {
                const curr = new Date(now);
                const firstday = new Date(curr.setDate(curr.getDate() - curr.getDay() + (curr.getDay() === 0 ? -6 : 1)));
                firstday.setHours(0,0,0,0);
                const lastday = new Date(firstday);
                lastday.setDate(lastday.getDate() + 6);
                lastday.setHours(23,59,59,999);
                return d >= firstday && d <= lastday;
            }

            // Itera sobre todos os itens brutos para contabilizá-los nas categorias de Semana, Mês e Ano
            rawItems.forEach(item => {
                const d = new Date(item.created_at);
                const isActive = item.is_active !== undefined ? item.is_active : true;

                // Processa e contabiliza os dados referentes ao período semanal
                if (isCurrentWeek(d)) {
                    let w = getMondayBasedDay(d);
                    if (datasetType !== 'single') {
                        if (isActive) weekAct[w]++; else weekInact[w]++;
                    } else {
                        weekTot[w]++;
                    }
                }

                // Processa e contabiliza os dados referentes ao período mensal atual
                if (d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth()) {
                    const day = d.getDate();
                    let idx = day <= 7 ? 0 : (day <= 14 ? 1 : (day <= 21 ? 2 : 3));
                    if (datasetType !== 'single') {
                        if (isActive) monthAct[idx]++; else monthInact[idx]++;
                    } else {
                        monthTot[idx]++;
                    }
                }

                // Processa e contabiliza os dados referentes ao período anual atual
                if (d.getFullYear() === now.getFullYear()) {
                    const m = d.getMonth();
                    if (datasetType !== 'single') {
                        if (isActive) yearAct[m]++; else yearInact[m]++;
                    } else {
                        yearTot[m]++;
                    }
                }
            });

            // Retorna um objeto estruturado contendo os rótulos e os valores mapeados para cada período
            return {
                dates: { week: labelsWeek, month: labelsMonth, year: labelsYear },
                values: {
                    week: datasetType !== 'single' ? { active: weekAct, inactive: weekInact } : weekTot,
                    month: datasetType !== 'single' ? { active: monthAct, inactive: monthInact } : monthTot,
                    year: datasetType !== 'single' ? { active: yearAct, inactive: yearInact } : yearTot
                }
            };
        }

        const processed = processData();

        // Instancia o objeto Chart.js do tipo linha para a exibição visual dos dados
        let chart = new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });

        // Atualiza dinamicamente os datasets e rótulos do gráfico conforme o período temporal selecionado
        function updateChart(period) {
            chart.data.labels = processed.dates[period] || [];
            const val = processed.values[period] || [];

            if (datasetType !== 'single') {
                chart.data.datasets = [
                    { label: 'Ativos', data: val.active || [], borderColor: '#007bff', 
                        backgroundColor: '#007bff', fill: false },
                    { label: 'Desativados / Inativos', data: val.inactive || [], 
                        borderColor: '#dc3545', backgroundColor: '#dc3545', fill: false }
                ];
            } else {
                chart.data.datasets = [
                    { label: 'Quantidade Criada', data: val, 
                        borderColor: '#007bff', backgroundColor: 'rgba(0,123,255,0.1)', fill: true }
                ];
            }
            chart.update();
        }

        // Define o estado inicial do gráfico utilizando o ano como padrão
        updateChart(select ? select.value : 'year');

        // Adiciona um listener no elemento select para atualizar o gráfico sempre que o filtro de período mudar
        if (select) {
            select.addEventListener('change', (e) => updateChart(e.target.value));
        }
    }

    // Inicializa os gráficos temporais na página para Usuários, Grupos e Despesas
    setupClientSideTemporalChart('usersTemporalChart', 'usersTemporalSelect', 'users-json-data', 'users');
    setupClientSideTemporalChart('groupsChart', 'groupsSelect', 'groups-json-data', 'groups');
    setupClientSideTemporalChart('expenseChart', 'expenseSelect', 'expenses-json-data', 'single');

    // Constrói e renderiza o gráfico de barras para exibição de membros aceitos e pendentes
    const membershipCanvas = document.getElementById('membershipChart');
    if (membershipCanvas) {
        const accepted = parseInt(membershipCanvas.dataset.accepted || 0);
        const pending = parseInt(membershipCanvas.dataset.pending || 0);
        new Chart(membershipCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Membros Aceitos', 'Pendentes'],
                datasets: [{ label: 'Quantidade', data: [accepted, pending], 
                            backgroundColor: ['#007bff', '#ffc107'] }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
        });
    }

    // Constrói e renderiza o gráfico em rosca para exibição de faturas quitados e pendentes
    const splitCanvas = document.getElementById('splitsChart');
    if (splitCanvas) {
        const paid = parseInt(splitCanvas.dataset.paid || 0);
        const unpaid = parseInt(splitCanvas.dataset.unpaid || 0);
        new Chart(splitCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Quitadas', 'Pendentes'],
                datasets: [{ data: [paid, unpaid], backgroundColor: ['#17a2b8', '#ffc107'] }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Configura o comportamento de redirecionamento e filtros na tela de divisão de despesas
    const expenseFilterSelect = document.getElementById('expenseFilterSelect');
    if (expenseFilterSelect) {
        expenseFilterSelect.addEventListener('change', function() {
            let url = new URL(window.location.href);
            if (this.value) {
                url.searchParams.set('expense_id', this.value);
            } else {
                url.searchParams.delete('expense_id');
            }
            window.location.href = url.toString();
        });
    }

    // Configura o comportamento de redirecionamento e filtros na tela de membros de grupos
    const groupFilterSelect = document.getElementById('groupFilterSelect');
    if (groupFilterSelect) {
        groupFilterSelect.addEventListener('change', function() {
            let url = new URL(window.location.href);
            if (this.value) {
                url.searchParams.set('group_id', this.value);
            } else {
                url.searchParams.delete('group_id');
            }
            window.location.href = url.toString();
        });
    }
});