$(document).ready(function() {
    function showSpinner() {
        $('.loading-spinner').show();
    }

    function hideSpinner() {
        $('.loading-spinner').hide();
    }

    // Handle PDF upload
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        showSpinner();
        $.ajax({
            url: '/upload_pdfs',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                $('#uploadStatus').html('<div class="alert alert-success">' + response.message + '</div>');
            },
            error: function(xhr) {
                $('#uploadStatus').html('<div class="alert alert-danger">' + xhr.responseJSON.error + '</div>');
            },
            complete: function() {
                hideSpinner();
            }
        });
    });

    // Handle Excel upload
    $('#excelForm').on('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        showSpinner();
        $.ajax({
            url: '/upload_excel',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                var link = document.createElement('a');
                link.href = window.URL.createObjectURL(new Blob([response], {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}));
                link.download = 'Ziraat_QnA_LLM_Responses.xlsx';
                link.click();
            },
            error: function(xhr) {
                $('#excelStatus').html('<div class="alert alert-danger">' + xhr.responseJSON.error + '</div>');
            },
            complete: function() {
                hideSpinner();
            }
        });
    });

    // Handle question submission
    $('#questionForm').on('submit', function(e) {
        e.preventDefault();
        var query = $('#query').val();
        showSpinner();
        $.ajax({
            url: '/ask_question',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ query: query }),
            success: function(response) {
                $('#questionStatus').html('<div class="alert alert-success">' + response.response + '</div>');
            },
            error: function(xhr) {
                $('#questionStatus').html('<div class="alert alert-danger">' + xhr.responseJSON.error + '</div>');
            },
            complete: function() {
                hideSpinner();
            }
        });
    });
});
