   // change label for payment__payment_type field

   function addDays(date, days) {
       var result = new Date(date);
       result.setDate(result.getDate() + days);
       return result;
   }

   var labels = document.getElementsByTagName('label');
   var label = null;
   var selectID = 'id_payment__payment_type';

   for (var i = 0; i < labels.length; i++)
       if (labels[i].htmlFor == selectID) {
           label = labels[i];
           break;
       }
   label.innerHTML = "Payment Type"
   document.getElementById("id_ordered_date_0").placeholder = "Date from";
   document.getElementById("id_ordered_date_0").type = "text";
   document.getElementById("id_ordered_date_1").placeholder = "Date to";
   document.getElementById("id_ordered_date_1").type = "text";
   var picker = new Pikaday({
       field: document.getElementById('id_ordered_date_0'),
       format: 'D/M/YYYY',
       toString(date, format) {
           // you should do formatting based on the passed format,
           // but we will just return 'D/M/YYYY' for simplicity
           date2 = addDays(date, 1);
           const day = date.getDate();
           const month = date.getMonth() + 1;
           const year = date.getFullYear();
           return `${year}-${month}-${day}`;
       },
       parse(dateString, format) {
           // dateString is the result of `toString` method
           const parts = dateString.split('/');
           const day = parseInt(parts[0], 10);
           const month = parseInt(parts[1], 10) - 1;
           const year = parseInt(parts[2], 10);
           return new Date(year, month, day);
       }

   });

   var picker2 = new Pikaday({
       field: document.getElementById('id_ordered_date_1'),
       format: 'D/M/YYYY',
       toString(date, format) {
           // you should do formatting based on the passed format,
           // but we will just return 'D/M/YYYY' for simplicity
           const day = date.getDate();
           const month = date.getMonth() + 1;
           const year = date.getFullYear();
           return `${year}-${month}-${day}`;
       },
       parse(dateString, format) {
           // dateString is the result of `toString` method
           const parts = dateString.split('/');
           const day = parseInt(parts[0], 10);
           const month = parseInt(parts[1], 10) - 1;
           const year = parseInt(parts[2], 10);
           return new Date(year, month, day);
       }

   });

   const beforeSelect = document.getElementById("id_ordered_date_0")
   const afterSelect = document.getElementById("id_ordered_date_1")

   // *** want to set 2nd field 'afterSelect' to 1 day later of 'beforeSelect' field value

   beforeSelect.addEventListener("change", function() {

       // afterSelect.value = beforeSelect.value;


   });