$(document).ready(function() {
	$('#utc-offset').val(moment().utcOffset());
   $('#datePicker')
       .datetimepicker({
       		format: "MM/DD/YYYY hh:mm A",
       		showTodayButton: true,
       		defaultDate: moment()
       })
       .on('change dp.change focusout', function(e) {
           // Revalidate the date field
           $('#eventForm').formValidation('revalidateField', 'Date');
       });
    $('#eventForm')
       .formValidation({
           framework: 'bootstrap',
           icon: {
               valid: 'glyphicon glyphicon-ok',
               invalid: 'glyphicon glyphicon-remove',
               validating: 'glyphicon glyphicon-refresh'
           },
           fields: {
               Date: {
                   validators: {
                       notEmpty: {
                           message: 'The date is required'
                       },
                       date: {
                           format: 'MM/DD/YYYY h:m A',
                           message: 'The date is not a valid'
                       }
                   }
               },
               Memo: {
                   validators: {
                       notEmpty: {
                           message: 'Memo must have content'
                       }
                   }
               }
           }
       });
       
       // Validate on start
       $('#eventForm').formValidation('revalidateField', 'Date');
       $('#eventForm').formValidation('revalidateField', 'Memo');
});