$(document).ready(function () {
    $('#pass-button').on("click", function(){
        $('#match-type-select').val($('#match-type').val()).trigger("change");
        $('#campaign-select').val($('#campaign').val()).trigger("change");
        $('#adgroup-select').val($('#adgroup').val()).trigger("change");
        $('#target-select').val($('#target-type').val()).trigger("change");
        $('#hotel-select').val($('#hotel').val()).trigger("change");
        $('#district-select').val($('#district').val()).trigger("change");
        $('#province-select').val($('#province').val()).trigger("change");
    })

    $('#campaign-select').on("change", function(){
        $('#adgroup-select').attr("disabled", false);
        $('#adgroup-select').find('option').hide();
        //add disabled for the other selects option for the new value
        if (this.value) {
            console.log(this.value);
            $('#adgroup-select').find("option[data-campaign='"+this.value+"']").show();
        }
    })

    $('#target-select').on("change", function(){
        var target_type = $(this).find(":selected").text().toLowerCase();
        if (target_type == "hotel"){
            $('#hotel-select').attr("disabled", false);
            $('#district-select').attr("disabled", true);
            $('#district-select').prop('selectedIndex',1);
            $('#province-select').attr("disabled", true);
            $('#province-select').prop('selectedIndex',1);
        }
        if (target_type == "district"){
            $('#district-select').attr("disabled", false);
            $('#hotel-select').attr("disabled", true);
            $('#hotel-select').prop('selectedIndex',1);
            $('#province-select').attr("disabled", true);
            $('#province-select').prop('selectedIndex',1);
        }
        if (target_type == "province"){
            $('#province-select').attr("disabled", false);
            $('#hotel-select').attr("disabled", true);
            $('#hotel-select').prop('selectedIndex',1);
            $('#district-select').attr("disabled", true);
            $('#district-select').prop('selectedIndex',1);
        }
        if (target_type == "none"){
            $('#hotel-select').attr("disabled", true);
            $('#hotel-select').prop('selectedIndex',1);
            $('#district-select').attr("disabled", true);
            $('#district-select').prop('selectedIndex',1);
            $('#province-select').attr("disabled", true);
            $('#province-select').prop('selectedIndex',1);
        }
    })
    
    $('#keyword-update-form').bind('submit', function () {
        $('#hotel-select').attr("disabled", false);
        $('#district-select').attr("disabled", false);
        $('#province-select').attr("disabled", false);
    });
});