$(() => {
  var portfolioName;
  var portfolioObjects = [];
  var marketID;
  var tab_menu = [
    { id: "1", title: "Markets" },
    { id: "2", title: "My portfolios" },
  ];

  $.getJSON("/GetMarkets", {}, function (data) {
    $("#menuTabs").show();
    $("#gridContainer").show();
    const dxMenuCase = $("#menuTabs > .tabs-container").dxTabs({
      dataSource: data.message,
      selectedIndex: 0,
      onSelectionChanged(data) {
        refreshMarketGrid();
        createTableGrid(data);
      },
    });

    createTableGrid(data);

    mainTabPanel = $("#tabpanel-container").dxTabPanel({
      items: tab_menu,
      selectedIndex: 0,
      loop: false,
      animationEnabled: true,
      swipeEnabled: true,
      onSelectionChanged(e) {
        if (e.addedItems[0].id == 1) {
          $("#menuTabs").show();
          $("#gridContainer").show();
          $("#gridMyPortfolios").hide();
          refreshMarketGrid();
        } else if (e.addedItems[0].id == 2) {
          $("#menuTabs").hide();
          $("#gridContainer").hide();
          $.getJSON("/GetMyPortfoliosPositions", {}, function (data) {
            createPortfolioGrid(data.data);
          });
        }
      },
    });

    var tabs = $("#tabpanel-container").find(".dx-tab");
    $(tabs[1]).css("background", "#257bfa");
    $(tabs[1]).css("color", "white");
  });

  function createTableGrid(data) {
    const market = data.addedItems;
    $.getJSON(
      "/GetCompanies",
      { idMarket: market == undefined ? 1 : market[0].id },
      function (data) {
        var iconFolder;
        var width;
        if (market == undefined || market[0].id == 1) {
          iconFolder = "assets/Images/Markets/Crypto/Icons/";
          width = 150;
          marketID = 1;
        } else {
          iconFolder = "assets/Images/Markets/MOEX/Icons/";
          width = 300;
          marketID = market[0].id;
        }
        $.getJSON("/GetMyPortfolios", {marketID : marketID}, function (dataPortfolios) {
          $("#gridContainer").dxDataGrid({
            dataSource: data.data,
            showBorders: false,
            showColumnHeaders: true,
            wordWrapEnabled: true,
            toolbar: {
              items: [
                "groupPanel",
                {
                  location: "before",
                  widget: "dxSelectBox",
                  options: {
                    width: 300,
                    acceptCustomValue: true,
                    elementAttr: { id: "cmbPortfolios" },
                    placeholder: 'Choose Portfolio or Create New',
                    dataSource: dataPortfolios.data,
                    displayExpr: "PortfolioName",
                    valueExpr: "PortfolioID",
                    onValueChanged(data) {
                      refreshMarketGrid();
                      choosingPortfolioNameFromCmb =data.component.option('selectedItem').PortfolioName;
                    },
                    onCustomItemCreating(data) {
                      if (!data.text) {
                        return;
                      }
                    },
                  },
                },
                {
                  location: "before",
                  widget: "dxButton",
                  options: {
                    text: "Manage",
                    width: 136,
                    elementAttr: { id: "btnManage" },
                    onClick(e) {
                      var btnUpdate = $("#btnManage").dxButton("instance");
                      if (portfolioName != "" && portfolioName != undefined) {
                        if (portfolioObjects.length != 0) {
                          if (btnUpdate.option("text") == "Manage") {
                            var dataPortfolio = {
                              marketID : marketID,
                              portfolioName: portfolioName,
                              data: portfolioObjects,
                            };
                            $.ajax({
                              type: "POST",
                              url: "/SavePortfolio",
                              data: JSON.stringify(dataPortfolio),
                              contentType: "application/json",
                              dataType: "json",
                              success: function (data) {
                                console.log(data);
                                if (data == "Duplicate name!") {
                                  DevExpress.ui.notify(
                                    "It is duplicate name!",
                                    "warning",
                                    500
                                  );
                                } else {
                                  openMyPortfoliosAfterAddingOrUpdating();
                                }
                              },
                            });
                          } else {
                            var cmbPortfolios =
                              $("#cmbPortfolios").dxSelectBox("instance");
                            var dataPortfolio = {
                              portfolioID: cmbPortfolios.option("value"),
                              data: portfolioObjects,
                            };
                            $.ajax({
                              type: "POST",
                              url: "/AddPositionToPortfolio",
                              data: JSON.stringify(dataPortfolio),
                              contentType: "application/json",
                              dataType: "json",
                              success: function (data) {
                                openMyPortfoliosAfterAddingOrUpdating();
                              },
                            });
                          }
                        } else {
                          DevExpress.ui.notify("Select object!", "warning", 500);
                        }
                      } else {
                        DevExpress.ui.notify(
                          "Portfolio name is empty!",
                          "warning",
                          500
                        );
                      }
                    },
                  },
                },
                "exportButton",
                "columnChooserButton",
                "searchPanel",
              ],
            },
            columns:
              market == undefined || market[0].id == 1
                ? [
                    {
                      dataField: "Icon",
                      caption: "Name",
                      width: width,
                      height: 70,
                      allowFiltering: false,
                      alignment: "left",
                      cssClass: "cellGridCompanies",
                      cellTemplate(container, options) {
                        $("<div>")
                          .attr({ class: "parent" })
                          .append(
                            $("<img>", {
                              src: iconFolder + options.value,
                              class: "iconCompanies",
                            })
                          )
                          .append(
                            $("<span>", {
                              text: options.data.Name,
                              class: "child",
                            })
                          )
                          .appendTo(container);
                      },
                    },
                    {
                      dataField: "current_price",
                      caption: "Current price",
                      alignment: "center",
                      allowSorting: false,
                      cssClass: "cellGridCompanies",
                    },
                    {
                      dataField: "high_24h",
                      caption: "High 24h",
                      alignment: "center",
                      allowSorting: false,
                      cssClass: "cellGridCompanies",
                    },
                    {
                      dataField: "low_24h",
                      caption: "Low 24h",
                      alignment: "center",
                      allowSorting: false,
                      cssClass: "cellGridCompanies",
                    },
                    {
                      dataField: "price_change_24h",
                      caption: "Price change 24h",
                      alignment: "center",
                      allowSorting: false,
                      cssClass: "cellGridCompanies",
                    },
                    {
                      dataField: "price_change_percentage_24h",
                      caption: "Price change, % 24h",
                      alignment: "center",
                      cssClass: "cellGridCompanies",
                      calculateCellValue: function (rowData) {
                        return parseFloat(rowData["price_change_percentage_24h"]);
                      },
                    },
                    {
                      dataField: "Add",
                      width: 70,
                      allowFiltering: false,
                      allowSorting: false,
                      alignment: "center",
                      cssClass: "cellGridCompanies",
                      cellTemplate(container, options) {
                        createSwitcher(container, options);
                      },
                    },
                  ]
                : [
                    {
                      dataField: "Icon",
                      width: width,
                      height: 70,
                      allowFiltering: false,
                      allowSorting: false,
                      alignment: "left",
                      cssClass: "cellGridCompanies",
                      cellTemplate(container, options) {
                        $("<div>")
                          .attr({ class: "parent" })
                          .append(
                            $("<img>", {
                              src: iconFolder + options.value,
                              class: "iconCompanies",
                            })
                          )
                          .append(
                            $("<span>", {
                              text: options.data.Name,
                              class: "child",
                            })
                          )
                          .appendTo(container);
                      },
                    },
                    {
                      dataField: "Ticker",
                      caption: "Ticker",
                      width: 120,
                      alignment: "center",
                      cssClass: "cellGridCompanies",
                    },
                    {
                      dataField: "Desc",
                      caption: "Title",
                      alignment: "center",
                      cssClass: "cellGridCompanies",
                    },
                    {
                      dataField: "Add",
                      width: 70,
                      allowFiltering: false,
                      allowSorting: false,
                      alignment: "center",
                      cssClass: "cellGridCompanies",
                      cellTemplate(container, options) {
                        createSwitcher(container, options);
                      },
                    },
                  ],
            onCellPrepared: function (e) {
              if (e.rowType === "data") {
                if (e.column.dataField === "current_price") {
                  e.cellElement.css({ color: "#53b854", "font-weight": "bold" });
                }
                if (
                  e.column.dataField === "low_24h" ||
                  e.column.dataField === "price_change_24h" ||
                  e.column.dataField === "high_24h"
                ) {
                  e.cellElement.css({ "font-weight": "bold" });
                }
                if (e.column.dataField === "price_change_percentage_24h")
                  if (e.value > 0)
                    e.cellElement.css({
                      color: "#53b854",
                      "font-weight": "bold",
                    });
                  else e.cellElement.css({ color: "red", "font-weight": "bold" });
              }
            },
          });
        });
      
      }
    );
  }

  function createSwitcher(container, options) {
    var defaultValue = false;
    const index = portfolioObjects.findIndex(
      (obj) => obj.CompanyID == options.data.Id
    );
    if (index > -1) {
      defaultValue = true;
    }

    $("<div>")
      .append($("<div>", { id: "switcher" + options.data.Id }))
      .appendTo(container);
    $("#switcher" + options.data.Id).dxSwitch({
      width: "40px",
      value: defaultValue,
      onValueChanged(data) {
        var cmbPortfolios = $("#cmbPortfolios").dxSelectBox("instance");
        portfolioName = cmbPortfolios.option("text");
        if (portfolioName != "" && portfolioName != undefined) {
          $.getJSON(
            "/CheckingPositionInPortfolio",
            { positionID: options.data.Id, portfolioName: portfolioName },
            function (result) {
              if ((result == "update" || result == "new") && data.value === true) {
                if (result == "update"){
                  var btnUpdate = $("#btnManage").dxButton("instance");
                  btnUpdate.option("text", "Update");
                }
                var company_json = {
                  PortfolioName: portfolioName,
                  CompanyID: options.data.Id,
                  Name: options.data.Name,
                  Quantity: 0,
                  Price: 0,
                  LotSize: 0,
                  Comission: 0,
                  Risk: 0,
                };
                portfolioObjects.push(company_json);
              } else {
                $("#switcher" + options.data.Id)
                  .dxSwitch("instance")
                  .option("value", false);
                  if (result != "update"){
                    DevExpress.ui.notify(result, "warning", 500);
                  }

                var cmpIndex = portfolioObjects.findIndex(
                  (obj) => obj.CompanyID == options.data.Id
                );

                if (cmpIndex > -1) {
                  // only splice array when item is found
                  portfolioObjects.splice(index, 1); // 2nd parameter means remove one item only
                }
                if (portfolioObjects.length < 1) {
                  console.log(portfolioObjects);
                }
              }
            }
          );
        } else {
          $("#switcher" + options.data.Id)
            .dxSwitch("instance")
            .option("value", false);
          DevExpress.ui.notify("Portfolio name is empty!", "warning", 500);
        }
      },
    });
  }

  // Функция проверки наличия портфелей у пользователя
  function isHavingPortfolio() {
    $.getJSON("/GetMyPortfoliosPositions", {}, function (data) {
      if (data.data.length > 0) {
        var tbp = $("#tabpanel-container").dxTabPanel("instance");
        tbp.option("selectedIndex", 1);
      }
    });
  }

  function openMyPortfoliosAfterAddingOrUpdating() {
    console.log('openMyPortfoliosAfterAddingOrUpdating');
    var dataGridPortfolio = $("#gridMyPortfolios").dxDataGrid("instance");
    dataGridPortfolio.option("dataSource", []);
    $.getJSON("/GetMyPortfoliosPositions", {}, function (data) {
      console.log('GetMyPortfoliosPositions');
      console.log(data);
      dataGridPortfolio.option("dataSource", data.data);
    });
    var tbp = $("#tabpanel-container").dxTabPanel("instance");
    tbp.option("selectedIndex", 1);
    portfolioName = [];
  }

  function updateMarkets() {
    var selectedMarket = $("#menuTabs > .tabs-container")
      .dxTabs("instance")
      .option("selectedIndex");
    if (selectedMarket == 0) {
      $.getJSON("/GetCompanies", { idMarket: 1 }, function (data) {
        $("#gridContainer")
          .dxDataGrid("instance")
          .option("dataSource", data.data);
      });
    }
  }

  function refreshMarketGrid() {
    portfolioObjects = [];
    var dataGridMarkets = $("#gridContainer").dxDataGrid("instance");
    dataGridMarkets.refresh();
    $.getJSON("/GetMyPortfolios", {marketID : marketID}, function (dataPortfolios) {
      var cmbPortfolios = $("#cmbPortfolios").dxSelectBox("instance");
      cmbPortfolios.option('dataSource', dataPortfolios.data);
      var cmbPortfolios = $("#cmbPortfolios").dxSelectBox("instance");
      cmbPortfolios.option('text', '')
    });
  }

  // Проверка на наличие портфолио у пользователя
  isHavingPortfolio();

  setInterval(updateMarkets, 180000);
});
