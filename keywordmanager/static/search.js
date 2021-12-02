$(document).ready(function () {
    table = $('#table-detail').DataTable({
        dom: 'lfrtip',
        'paging': true,
        'columnDefs': [
         {
            orderable: false,
            className: 'select-checkbox',
            targets: 0
         }],
        'select': {
            'style': 'multi'
        },
        'order': [[1, 'asc']]
    });

    $('#campaign_input').on("change", function(){
        localStorage.setItem('campaign', this.value);

        $('#adgroup_input').find('option').hide();
        $('#adgroup_input option[value="Tất cả"]').show();
        //add disabled for the other selects option for the new value
        if (this.value) {
            console.log(this.value);
            $('#adgroup_input').find("option[data-campaign='"+this.value+"']").show();
            $('#adgroup_input').val("Tất cả").trigger("change");
        }
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

    $('#submit-table-data-button').on('click', function(e){
        var tblData = table.rows('.selected').data();
        var data = [];
        var tmpData;
        $.each(tblData, function(i, val) {
            tmpData = tblData[i];
            data.push({id: tmpData[1], type_id: tmpData[3], type: tmpData[5]});
        });

        if(data.length > 0) {
			$.ajax({
				type: "POST",
				contentType: 'application/json;charset=UTF-8',
				url: "/search/delete",
				data: JSON.stringify({ 'data': data }),
				cache: false,
				success: function(msg) {
					location.reload();
				},
				error: function(jqXHR, textStatus, errorThrown) {
				    console.log(errorThrown);
				}
			})
		} else {
		    alert('Please select before delete.');
		}
    });
});