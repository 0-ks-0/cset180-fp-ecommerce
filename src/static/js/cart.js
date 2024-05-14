function addToCart(id)
{
	$.ajax
	({
		url: '/products',
		type: 'POST',
		contentType: 'application/json',
		data: JSON.stringify({'product_id': id}),
		success: function(message)
		{
			const message_div = document.querySelector("#message")

			if (!message_div) return

			// Display message div if it is not showing
			if (message_div.style.display == "none")
			{
				message_div.style.display = "block"
			}

			message_div.innerHTML = message

			// Hide message div after 1s
			setTimeout(() =>
			{
				message_div.style.display = "none"
			}, 1000)
		}
	})
}

/*
*	Cart page
*/
function removeItem(element, cart_item_id)
{
	element.parentElement.remove()

	fetch(`/cart`, {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "DELETE",
		body: JSON.stringify({
			"cart_item_id": cart_item_id
		})
	})
	.then(function (response) // Callback function when response sent from server
	{
		if (!response.ok)
		{
			throw Error(`Error: ${response.status || response.statusText}`)
		}
	})
	.catch(error => // Catch errors from sending / receiving
	{
		console.log(error)
	})
}

function updateItemQuantity(element, cart_item_id)
{
	console.log("updateing")
	fetch(`/cart`, {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "PATCH",
		body: JSON.stringify({
			"cart_item_id": cart_item_id,
			"quantity": parseInt(element.value)
		})
	})
	.then(function (response) // Callback function when response sent from server
	{
		if (!response.ok)
		{
			throw Error(`Error: ${response.status || response.statusText}`)
		}
	})
	.catch(error => // Catch errors from sending / receiving
	{
		console.log(error)
	})
}


function placeOrder(event, cart_id)
{
	event.preventDefault()

	const form = document.querySelector("#cart_form")

	if (!form) return

	const form_data = new FormData(form)

	// Get data on address
	const address_data = {}

	address_data["street"] = form_data.get("street_address")
	address_data["city"] = form_data.get("city")
	address_data["state"] = form_data.get("state")
	address_data["zip_code"] = form_data.get("zip_code")
	address_data["country"] = form_data.get("country")

	/*
	Format of data passed in body
	{
		"cart_id": 0.
		"address_data": {
			"street": "",
			"city": "",
			"state": "",
			"zip_code": "",
			"country": ""
		}
		"payment_method": ""
	}
	*/

	fetch(`/cart`, {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "POST",
		body: JSON.stringify({
			"cart_id": cart_id,
			"address_data": address_data,
			"payment_method": form_data.get("payment")
		})
	})
	.then(function (response) // Callback function when response sent from server
	{
		// Check if status code between 200 and 300
		if (response.ok)
		{
			return response.json() // Convert response from server to json

			.then(response =>
			{
				alert(response.message)
				top.location = response.url
			})
		}
		else
		{
			throw Error(`Error: ${response.status || response.statusText}`)
		}
	})
	.catch(error => // Catch errors from sending / receiving
	{
		console.log(error)
	})
}
