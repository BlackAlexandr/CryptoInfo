function createPortfolioGrid(data) {
  
  const dataSource = [{
    country: 'USA',
    hydro: 71.2,
    oil: 910.4,
    gas: 483.2,
    coal: 564.3,
    nuclear: 216.1,
  }, {
    country: 'China',
    hydro: 72.5,
    oil: 223.6,
    gas: 36,
    coal: 956.9,
    nuclear: 11.3,
  }, {
    country: 'Russia',
    hydro: 47.7,
    oil: 149.4,
    gas: 432.3,
    coal: 105,
    nuclear: 29.3,
  }, {
    country: 'Japan',
    hydro: 17.9,
    oil: 283.6,
    gas: 61.8,
    coal: 120.8,
    nuclear: 52.8,
  }, {
    country: 'India',
    hydro: 14.4,
    oil: 86.4,
    gas: 25.1,
    coal: 204.8,
    nuclear: 3.8,
  }, {
    country: 'Germany',
    hydro: 6.6,
    oil: 101.7,
    gas: 92.7,
    coal: 85.7,
    nuclear: 30.8,
  }];

  var position = {};
  var selectedPortfolioID;
  $("#gridMyPortfolios").show();
  $("#menuTabs").hide();
  $("#gridContainer").hide();
  const dataGrid = $("#gridMyPortfolios")
    .dxDataGrid({
      dataSource: data,
      keyExpr: "ID",
      focusedRowEnabled: true,
      allowColumnReordering: true,
      width: "100%",
      showBorders: true,
      showColumnLines: true,
      showRowLines: true,
      rowAlternationEnabled: true,
      
      editing: {
        mode: "cell",
        allowUpdating: true,
        allowDeleting: true,
        allowAdding: true,
      },
      grouping: {
        autoExpandAll: true,
      },
      searchPanel: {
        visible: true,
      },
      groupPanel: {
        visible: true,
      },
      selection: {
        mode: 'single',
      },
      onSelectionChanged(e) {
        e.component.collapseAll(-1);
        e.component.expandRow(e.currentSelectedRowKeys[0]);
        console.log(e);
      },
      onContentReady(e) {
        if (!e.component.getSelectedRowKeys().length) { e.component.selectRowsByIndexes(0); }
      },
      onRowClick(e) {
        console.log(e.data.items);
        selectedPortfolioID = e.data.items[0]["PortfolioID"];
      },
      masterDetail: {
        enabled: false,
        template(container, options) {
          const currentEmployeeData = options.data;
          container.append($(`<div class="employeeInfo"><p class="employeeNotes">${currentEmployeeData.Name}</p></div><div id='chart'><div>`));
          const chart = $('#chart').dxChart({
            palette: 'Violet',
            dataSource,
            commonSeriesSettings: {
              argumentField: 'country',
              type: 'line',
            },
            margin: {
              bottom: 20,
            },
            argumentAxis: {
              valueMarginsEnabled: false,
              discreteAxisDivisionMode: 'crossLabels',
              grid: {
                visible: true,
              },
            },
            series: [
              { valueField: 'hydro', name: 'Hydro-electric' },
              { valueField: 'oil', name: 'Oil' },
              { valueField: 'gas', name: 'Natural gas' },
              { valueField: 'coal', name: 'Coal' },
              { valueField: 'nuclear', name: 'Nuclear' },
            ],
            legend: {
              verticalAlignment: 'bottom',
              horizontalAlignment: 'center',
              itemTextPosition: 'bottom',
            },
            title: {
              text: 'Energy Consumption in 2004',
              subtitle: {
                text: '(Millions of Tons, Oil Equivalent)',
              },
            },
            export: {
              enabled: true,
            },
            tooltip: {
              enabled: true,
            },
          }).dxChart('instance');
        },
      },
      onCellPrepared: function (e) {
        if (e.rowType === "data") {
          if (e.column.dataField === "Name")
            e.cellElement.css({ "font-weight": "bold" });
        }
      },
      onRowRemoving(e) {
        var deferred = $.Deferred();
        $.ajax({
          url: `/RemovePosition?idPosition=${e.key}`,
          success: function (validationResult) {
            if (validationResult.errorText) {
              deferred.reject(validationResult.errorText);
            } else {
              deferred.resolve(false);
            }
          },
          error: function () {
            deferred.reject("Data Loading Error");
          },
          timeout: 5000,
        });
        e.cancel = deferred.promise();
      },
      onRowUpdating(e) {
        position = {
          ID: e.key,
          Quantity:
            e.newData["Quantity"] != undefined
              ? e.newData["Quantity"]
              : e.oldData["Quantity"],
          Price:
            e.newData["Price"] != undefined
              ? e.newData["Price"]
              : e.oldData["Price"],
          LotSize:
            e.newData["LotSize"] != undefined
              ? e.newData["LotSize"]
              : e.oldData["LotSize"],
          Comission:
            e.newData["Comission"] != undefined
              ? e.newData["Comission"]
              : e.oldData["Comission"],
          Risk:
            e.newData["Risk"] != undefined
              ? e.newData["Risk"]
              : e.oldData["Risk"],
        };

        $.ajax({
          url: "/UpdatePosition",
          type: "POST",
          data: JSON.stringify(position),
          contentType: "application/json",
          dataType: "json",
          success: function (result) {
          },
          error: function () {
            deferred.reject("Data Loading Error");
          },
          timeout: 5000,
        });
      },
      columns: [
        { dataField: "Name", allowEditing: false },
        {
          dataField: "Quantity",
          dataType: "number",
          caption: "Quantity",
          allowSorting: false,
          validationRules: [
            { type: "required", message: "Quantity input required." },
          ],
        },
        {
          dataField: "Price",
          dataType: "number",
          caption: "Price",
          allowSorting: false,
          validationRules: [
            { type: "required", message: "Price input required." },
          ],
        },
        {
          dataField: "LotSize",
          dataType: "number",
          caption: "LotSize",
          allowSorting: false,
          validationRules: [
            { type: "required", message: "LotSize input required." },
          ],
        },
        {
          dataField: "Comission",
          dataType: "number",
          caption: "Comission",
          allowSorting: false,
          validationRules: [
            { type: "required", message: "Comission input required." },
          ],
        },
        {
          dataField: "Risk",
          dataType: "number",
          allowSorting: false,
          caption: "Risk",
          validationRules: [
            { type: "required", message: "Risk input required." },
          ],
        },
        {
          dataField: "PortfolioID",
          visible: false
        },
        {
          dataField: "PortfolioName",
          groupIndex: 0,
        },
      ],
      toolbar: {
        items: [
          {
            location: "after",
            widget: "dxButton",
            options: {
              text: "Delete",
              width: 136,
              onClick(e) {
                if (selectedPortfolioID !== undefined) {
                  const promptPromise = DevExpress.ui.dialog.confirm("Are you sure?", "Delete portfolio");
                  promptPromise.done((dialogResult) => {
                  if (dialogResult) {
                    $.ajax({
                      url: `/RemovePortfolio?portfolioID=${selectedPortfolioID}`,
                      success: function (data) {
                        $.getJSON("/GetMyPortfoliosPositions", {}, function (data) {
                          var dataGrid =
                            $("#gridMyPortfolios").dxDataGrid("instance");
                          dataGrid.option("dataSource", data.data);
                        });
                        var myDialog = DevExpress.ui.dialog.custom({
                          title: "SUCCESS!",
                          messageHtml: "Success reemove item!",
                          buttons: [
                            {
                              text: "OK",
                              onClick: function (e) {
                                myDialog.hide();
                              },
                            },
                          ],
                        });
                        myDialog.show();
                        setTimeout(function () {
                          myDialog.hide();
                        }, 1200);
                      },
                      error: function () {
                        deferred.reject("Data Loading Error");
                      },
                      timeout: 5000,
                    });
                  }
                  });
                }
              },
            },
          },
          "searchPanel",
        ],
      },
    })
    .dxDataGrid("instance");

  $("#autoExpand").dxCheckBox({
    value: true,
    text: "Expand All Groups",
    onValueChanged(data) {
      dataGrid.option("grouping.autoExpandAll", data.value);
    },
  });
}
