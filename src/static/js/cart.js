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
