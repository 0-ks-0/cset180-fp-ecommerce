function deleteProduct(url, product_id)
{
	fetch(`${url}`, {
		headers:
		{
			"Accept": "application/json",
			"Content-Type" : "application/json"
		},
		method: "DELETE",
		body: JSON.stringify
		({
			"product_id": product_id
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
				// Not working
				if(response.redirected)
				{
					window.location = response.url
				}

				window.location = response.response
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

function createWarranty()
{
	const warranty_div = document.querySelector("#warranties")

	if (!warranty_div) return

	const div = document.createElement("div")
	div.classList.add("warranty_container")
	div.classList.add("flex_column")

	const days = document.createElement("input")
	days.setAttribute("type", "number")
	days.name =  "coverage_days"
	days.placeholder = "Coverage Days"
	days.required = true
	days.setAttribute("min", "1")
	days.setAttribute("step", "1")
	days.onkeypress = (event) =>
	{
		return (event.charCode != 8 && event.charCode == 0 || (event.charCode >= 48 && event.charCode <= 57))
	}

	const textarea = document.createElement("textarea")
	textarea.name = "coverage_info"
	textarea.placeholder = "Coverage Info"
	textarea.required = true

	div.appendChild(days)
	div.appendChild(textarea)

	warranty_div.appendChild(div)
}
