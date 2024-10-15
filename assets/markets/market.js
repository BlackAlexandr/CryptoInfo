$(() => {
    let ticker = 'AA';

    $.getJSON("/GetMarketsData", {}, function (data) {
      console.log(data);
        $("#gridCompanies").dxDataGrid({
            dataSource: data.data,
            showBorders: true,
            showColumnHeaders: true,
            wordWrapEnabled: true,
            scrolling: {
              rowRenderingMode: 'virtual',
            },
            paging: {
              pageSize: 1000,
            },
            pager: {
              visible: false,
              allowedPageSizes: [5, 10, 'all'],
            },
            columns: ['Stocks', 'Equities', 'Created', 'StartItems', 'StartVolume', 'EnterPrice', 'CurItems', 'LastPrice', 'PriceChanged', 'ProfitAbs', 'Profit'],
            selection: {
                mode: 'single',
              },
              onSelectionChanged(e) {
                e.component.collapseAll(-1);
                e.component.expandRow(e.currentSelectedRowKeys[0]);
              },
              masterDetail: {  
                enabled: true,
                template(container, options) {
                    container.append($(`<div id='chart'><div>`));
                    var chart = $('#chart').dxChart({
                      commonSeriesSettings: {
                        argumentField: 'time',
                        type: 'line',
                      },
                      margin: {
                        bottom: 20,
                      },
                      argumentAxis: {
                        grid: {
                          visible: true,
                        },
                        label: {
                          customizeText() {
                            return this.valueText.slice(0, 10);
                          },
                        },  
                      },
                      series: [
                        { valueField: 'profit', name: 'Profit,%: ', color: 'green' },
                        { valueField: 'changeT0', name: options.row.data.Stocks + ',%: ', color: 'blue' }
                      ],
                      legend: {
                        verticalAlignment: 'bottom',
                        horizontalAlignment: 'center',
                        itemTextPosition: 'bottom',
                      },
                      loadingIndicator: {
                        enabled: true
                      },
                      title: {
                        text: options.row.data.Equities,
                      },
                      tooltip: {
                        enabled: true,
                        customizeTooltip(arg) {
                          console.log(arg);
                          return {
                            text: `${arg.argumentText}<br/>${arg.valueText}`,
                          };
                      },
                    }
                    }).dxChart('instance');

                    chart.showLoadingIndicator();

                    $.getJSON("/GetGraphData", {ticker : options.row.data.Stocks}, function (data) {          
                        chart.hideLoadingIndicator();
                        const series =  [
                          { valueField: 'profit', name: 'Profit,%: ' + data.data[data.data.length - 1].legendaAlgo, color: 'green' },
                          { valueField: 'changeT0', name: options.row.data.Stocks + ',%: ' + data.data[data.data.length - 1].legendaQuote, color: 'blue' }
                        ];
                        const dataSource = data.data;
                        chart.option("dataSource", dataSource);
                        chart.option("series", series);  
                    });
                },
              },
          });

    });

});
