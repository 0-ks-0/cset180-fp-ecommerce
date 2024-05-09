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

/*
*	Create product page
*/

/**
 * Format
 * {
 * 	"vendor_id": "0" or ""
 * 	"name": "",
 * 	"description": "",
 * 	"quantity": "0",
 * 	"price": "0.00",
 * 	"images": ["", ""] or [],
 * 	"warranties": [{"coverage_days" : 0, "coverage_info": ""}] or []
 * }
 * @returns Object
 */
function getProductData()
{
	// Message to display if there is no value in input
	const message = document.querySelector("#message")
	if (!message)
	{
		message = document.createElement("div")

		const container = document.querySelector(".page_body")
		if (!container) return

		container[0].appendChild(message)
	}

	const data = {}

	// TODO make sure there actually is value in the input

	// Vendor ID
	const vendor_id = document.getElementsByName("vendor_id")

	if (vendor_id.length < 1)
		data.vendor_id = ""

	else
		data.vendor_id = vendor_id[0].value

	// Info
	const name = document.getElementsByName("name")
	if (!name) return
	data.name = name[0].value

	const description = document.getElementsByName("description")
	if (!description) return
	data.description = description[0].value

	const quantity = document.getElementsByName("quantity")
	if (!quantity) return
	data.quantity = quantity[0].value

	const price = document.getElementsByName("price")
	if (!price) return
	data.price = price[0].value

	// Images
	const images = document.getElementsByName("image")
	if (!images)
		data.images = []
	else
	{
		const image_links = []

		for (const link of images)
		{
			// Add if there is a link
			if (link.value)
				image_links.push(link.value)
		}

		data.images = image_links
	}

	// Warranties
	const warranties = []
	const warranty_days = document.getElementsByName("coverage_days")
	const coverage_info = document.getElementsByName("coverage_info")

	// TODO maybe check to make sure length of warranty_days and coverage_info is the same

	for(let i = 0; i < warranty_days.length; i++)
	{
		// Add if there is coverage info
		if (coverage_info[i].value)
			warranties.push({
				"coverage_days": warranty_days[i].value,
				"coverage_info": coverage_info[i].value
			})
	}

	data.warranties = warranties

	return data
}

function createProduct()
{
	data = getProductData()
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
