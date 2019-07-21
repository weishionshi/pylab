var clsf;

$(document).ready(function () {

    init();


});


function init() {
    $.ajax({
        type: "GET",
        contentType: "application/json;charset=UTF-8",
        url: "init/",
        data: {},
        success: function (result) {
            clsf = result.data;
            for(let i=0;i<clsf.length;i++){
                let node = clsf[i];
                if(node.superiorCode == "0") {
                    let option = document.createElement("option");
                    option.value = node.code;
                    option.text = node.name;
                    $("#cl1").append(option);
                }
            }
            setCl2();
        },
        error: function (e) {
            console.log(e.status);
        }
    });

}

function setCl2(){
    $("#cl2").empty();

    let code = $("#cl1").val();
    for(let i=0;i<clsf.length;i++){
        if(code == clsf[i].superiorCode){
            let option = document.createElement("option");
            option.value = clsf[i].code;
            option.text = clsf[i].name;
            $("#cl2").append(option);
        }
    }
}
