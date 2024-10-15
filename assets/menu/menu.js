$(() => {
    $.getJSON("/getMenu", {}, function (data) {    
        const menu = $("#menu").dxMenu({
            items: data,
            adaptivityEnabled: true,
            rtlEnabled: true,
        }).dxMenu('instance');
    });    
});