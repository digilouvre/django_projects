   var stripe = Stripe('pk_test_51IALXjJ9OrFClkteHc70SQtGsoB84UDEpGxXxf5JH8keyn8eKOJQQ75NJTUzzRQiwbc2it9hSFqKAOpxXO08j1IP00F0CE4qZu');



  // Create an instance of Elements.
  var elements = stripe.elements();

  // Custom styling can be passed to options when creating an Element.
  // (Note that this demo uses a wider set of styles than the guide below.)
  var style = {
    base: {
      color: '#32325d',
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: 'antialiased',
      fontSize: '16px',
      '::placeholder': {
        color: '#aab7c4'
      }
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a'
    }
  };

  // Create an instance of the card Element.
  var card = elements.create('card', {style: style});

  // Add an instance of the card Element into the `card-element` <div>.
  card.mount('#card-element');

  // Handle real-time validation errors from the card Element.
  card.addEventListener('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
      displayError.textContent = event.error.message;
    } else {
      displayError.textContent = '';
    }
  });

  // Handle form submission.
  var form = document.getElementById('stripe-form');
  form.addEventListener('submit', function(event) {
    event.preventDefault();

    stripe.createToken(card).then(function(result) {
      if (result.error) {
        // Inform the user if there was an error.
        var errorElement = document.getElementById('card-errors');
        errorElement.textContent = result.error.message;
        //window.alert("error: ", result.error.message);
      } else {
        // Send the token to your server.
        stripeTokenHandler(result.token);
        // window.alert("token: ", result.token);
      }
    });
  });

  // Submit the form with the token ID.
  function stripeTokenHandler(token) {
    // Insert the token ID into the form so it gets submitted to the server
    var form = document.getElementById('stripe-form');
    var hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'stripeToken');
    hiddenInput.setAttribute('value', token.id);
    form.appendChild(hiddenInput);
    // window.alert("form sent");
    // Submit the form
    form.submit();
  }

  var currentCardForm = $('.current-card-form');
  var newCardForm = $('.new-card-form');
  var use_default_card = document.querySelector("input[name=use_default_card]");
  use_default_card.addEventListener('change', function() {
    if (this.checked) {
      newCardForm.hide();
      currentCardForm.show()
    } else {
      newCardForm.show();
      currentCardForm.hide()
    }
  });
