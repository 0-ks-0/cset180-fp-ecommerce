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
