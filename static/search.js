$(document).ready(function () {
    $('#table-detail').DataTable({
        dom: 'Bfrtip',
        "bLengthChange": false,
        buttons: [
            'csv',
        ],
        select: true
    });

    $('#campaign-input').on("change", function(){
        var campaign_name = $(this).find(":selected").text();
        if (campaign_name == "None"){
            $('#campaign-select').attr("disabled", false);
            $('#adgroup-select').attr("disabled", true);
            $('#adgroup-select option[value="None"]').prop('selected', true).change();
        }
    });

    $('#campaign_input').on("change", function(){
        localStorage.setItem('campaign', this.value);
    });
    if(localStorage.getItem('campaign')){
        $('#campaign_input').val(localStorage.getItem('campaign'));
    }

    $('#adgroup_input').on("change", function(){
        localStorage.setItem('adgroup', this.value);
    });
    if(localStorage.getItem('adgroup')){
        $('#adgroup_input').val(localStorage.getItem('adgroup'));
    }

    $('#district_input').on("change", function(){
        localStorage.setItem('district', this.value);
    });
    if(localStorage.getItem('district')){
        $('#district_input').val(localStorage.getItem('district'));
    }

    $('#province_input').on("change", function(){
        localStorage.setItem('province', this.value);
    });
    if(localStorage.getItem('province')){
        $('#province_input').val(localStorage.getItem('province'));
    }

    $('#hotel_input').on("change", function(){
        localStorage.setItem('hotel', this.value);
    });
    if(localStorage.getItem('hotel')){
        $('#hotel_input').val(localStorage.getItem('hotel'));
    }

    $('#kwtype_input').on("change", function(){
        localStorage.setItem('kwtype', this.value);
    });
    if(localStorage.getItem('kwtype')){
        $('#kwtype_input').val(localStorage.getItem('kwtype'));
    }
});