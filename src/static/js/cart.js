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

function checkout(event, cart_id)
{
	event.preventDefault()

	const pageBody = document.querySelector(".page_body")

	if (!pageBody) return

	// Form for placing order
	const form = document.createElement("form")
	form.classList.add("flex_column")
	form.id = "order_form"

	// Form header
	const header = document.createElement("h3")
	header.innerHTML = "Almost there"

	// Container to hold address info
	const addressDiv = document.createElement("div")
	addressDiv.classList.add("flex_column")
	addressDiv.id = "address_container"

	const streetAddress = document.createElement("input")
	streetAddress.setAttribute("type", "text")
	streetAddress.name = "street_address"
	streetAddress.placeholder = "Street Address"
	streetAddress.required = true

	const city = document.createElement("input")
	city.setAttribute("type", "text")
	city.name = "City"
	city.placeholder = "City"
	city.required = true

	const state = document.createElement("input")
	state.setAttribute("type", "text")
	state.name = "State"
	state.placeholder = "State"
	state.required = true

	const zipCode = document.createElement("input")
	zipCode.setAttribute("type", "text")
	zipCode.name = "Zip Code"
	zipCode.placeholder = "Zip Code"
	zipCode.required = true

	const country = document.createElement("input")
	country.setAttribute("type", "text")
	country.name = "Country"
	country.placeholder = "Country"
	country.required = true

	const row = document.createElement("div")
	row.classList.add("flex_row")

	row.appendChild(state)
	row.appendChild(zipCode)

	addressDiv.appendChild(streetAddress)
	addressDiv.appendChild(city)
	addressDiv.appendChild(row)
	addressDiv.appendChild(country)

	// Payment section
	const paymentDiv = document.createElement("div")
	paymentDiv.classList.add("flex_row")
	paymentDiv.id = "payment_container"

	const paymentLabel = document.createElement("label")
	paymentLabel.setAttribute("for", "payment")
	paymentLabel.innerHTML = "Payment Method"

	// Select element for payment
	const paymentSelect = document.createElement("select")
	paymentSelect.name = "payment"
	paymentSelect.id = "payment"

	// Create options for select element
	const paymentOptions = ["Card", "Other digital method"]

	for (let i = 0; i < paymentOptions.length; i++)
	{
		const option = document.createElement("option")
		option.value = paymentOptions[i]
		option.text = paymentOptions[i]

		paymentSelect.appendChild(option)
	}

	// TODO create inputs for card info if "Card" payment option selected

	paymentDiv.appendChild(paymentLabel)
	paymentDiv.appendChild(paymentSelect)

	const submit = document.createElement("input")
	submit.setAttribute("type", "submit")
	submit.value = "Place Order"
	submit.addEventListener("submit", (event) =>
	{
		placeOrder(event, cart_id)
	})

	form.appendChild(header)
	form.appendChild(addressDiv)
	form.appendChild(paymentDiv)
	form.appendChild(submit)

	pageBody.appendChild(form)
}
