function get_patient(url) {
    // obtiene los datos de una persona con la api rest-framewowrk
    $.ajax({
        type: "GET",
        // url: "/app/api/patients/"+id+"/?format=json",
        url: url,
        dataType: "json",
        success: function(data) {
            console.log(data)
            dato = data
            $("#id_patient").val(data.id)
            $("#id_full_name").val(data.full_name)
            $("#id_dni").val(data.dni)
            $("#id_gender").val(data.gender)
            $("#id_phone").val(data.phone)
            $("#id_job").val(data.job)

            $("#prescription_form *").attr('disabled', 'disabled');
        }, //End of AJAX Success function
    });


}



function update_patient() {
    if ($("#id_full_name").attr("disabled") == "disabled") {
        $("#prescription_form *").removeAttr('disabled');
    } else {
        let ruta_update = $("#id_patient").data("url-update")
        ruta_update = ruta_update.substring(0, ruta_update.length - 2) + $("#id_patient").val() + "/"

        let datos = $("#prescription_form").serialize()

        $.ajax({
            type: "PATCH",
            url: ruta_update,
            dataType: "json",
            data: datos,
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            success: function(data) {
                location.reload()
                console.log(data)

            }, //End of AJAX Success function
        }).fail(function(e) {
            console.log(e.message)
        });

    }

}







function delete_patient() {
    let ruta_delete = $("#id_patient").data("url-delete")
    ruta_delete = ruta_delete.substring(0, ruta_delete.length - 2) + $("#id_patient").val() + "/"
    console.log(ruta_delete)

    $.ajax({
        type: "DELETE",
        url: ruta_delete,
        dataType: "json",
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function(data) {
            location.reload()
            console.log(data)

        }, //End of AJAX Success function
    }).fail(function(e) {
        console.log(e.message)
    });
}