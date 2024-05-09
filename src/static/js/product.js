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

function createImage()
{
	const images_div = document.querySelector("#images")

	if (!images_div) return

	const add_button = document.querySelector("#images .add_button")

	if (!add_button) return

	// Container for link and delete button
	const div = document.createElement("div")
	div.classList.add("image_container")
	div.classList.add("flex_row")

	// Input for image link
	const input = document.createElement("input")
	input.setAttribute("type", "text")
	input.name = "image"
	input.placeholder = "Image Link"

	// Button to delete
	const deleteButton = document.createElement("button")
	deleteButton.classList.add("delete_button")
	deleteButton.innerHTML = "Delete"
	deleteButton.onclick = () =>
	{
		images_div.removeChild(div)
	}

	div.appendChild(input)
	div.appendChild(deleteButton)

	images_div.insertBefore(div, add_button)
}

function createWarranty()
{
	const warranty_div = document.querySelector("#warranties")

	if (!warranty_div) return

	const add_button = document.querySelector("#warranties .add_button")

	if (!add_button) return

	// Container for warranty
	const div = document.createElement("div")
	div.classList.add("warranty_container")
	div.classList.add("flex_row")

	const info_div = document.createElement("div")
	info_div.id = "warranty_info_div"
	info_div.classList.add("flex_column")

	// Coverage days
	const days = document.createElement("input")
	days.setAttribute("type", "number")
	days.name =  "coverage_days"
	days.placeholder = "Coverage Days"
	days.setAttribute("min", "1")
	days.setAttribute("step", "1")
	days.onkeypress = (event) =>
	{
		return (event.charCode != 8 && event.charCode == 0 || (event.charCode >= 48 && event.charCode <= 57))
	}

	// Coverage info
	const textarea = document.createElement("textarea")
	textarea.name = "coverage_info"
	textarea.placeholder = "Coverage Info"
	textarea.required = true

	// Button to delete
	const deleteButton = document.createElement("button")
	deleteButton.classList.add("delete_button")
	deleteButton.innerHTML = "Delete"
	deleteButton.onclick = () =>
	{
		warranty_div.removeChild(div)
	}

	info_div.appendChild(days)
	info_div.appendChild(textarea)

	div.appendChild(info_div)
	div.appendChild(deleteButton)

	warranty_div.insertBefore(div, add_button)
}
