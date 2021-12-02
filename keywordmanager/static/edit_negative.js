$(document).ready(function () {
    $('#pass-button').on("click", function(){
        $('#match-type-select').val($('#match-type').val()).trigger("change");
        $('#level-select').val($('#level').val()).trigger("change");
        $('#campaign-select').val($('#campaign').val()).trigger("change");
        $('#adgroup-select').val($('#adgroup').val()).trigger("change");
    })

    $('#level-select').on("change", function(){
        var campaign_name = $(this).find(":selected").text();
        if (campaign_name == "campaign"){
            $('#campaign-select').attr("disabled", false);
            $('#adgroup-select').attr("disabled", true);
            $('#adgroup-select option[value="None"]').prop('selected', true).change();
        }
        if (campaign_name == "adgroup"){
            $('#campaign-select').attr("disabled", false);
            $('#adgroup-select').attr("disabled", false);
            $('#campaign-select option[value="None"]').prop('selected', true).change();
        }
    })

    $('#keyword-update-form').bind('submit', function () {
        $('#campaign-select').attr("disabled", false);
        $('#adgroup-select').attr("disabled", false);
    });

    $('#campaign-select').change(function() {
        $('#adgroup-select').find('option').hide();
        //add disabled for the other selects option for the new value
        if (this.value) {
            console.log(this.value);
            $('#adgroup-select').find("option[data-campaign='"+this.value+"']").show();
        }
    });
});