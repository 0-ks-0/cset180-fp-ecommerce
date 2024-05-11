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
	data.name = name[0].value

	const description = document.getElementsByName("description")
	data.description = description[0].value

	const quantity = document.getElementsByName("quantity")
	if (!quantity[0].value)
		data.quantity = "0"
	else
		data.quantity = quantity[0].value

	const price = document.getElementsByName("price")
	console.log(price)
	if (!price[0].value)
		data.price = "0.00"
	else
		data.price = price[0].value

	// Images
	const images = document.getElementsByName("image")

	const image_links = []

	for (const link of images)
	{
		// Add if there is a link
		if (link.value)
			image_links.push(link.value)
	}

	data.images = image_links

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

function createProduct(account_type)
{
	data = getProductData()

	// Make sure Vendor ID is inputted by admin
	if (account_type == "admin" && !data.vendor_id)
	{
		const message = document.querySelector("#message")

		message.innerHTML = "Vendor ID required"

		return
	}

	fetch("/products/create", {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "POST",
		body: JSON.stringify(data)
	})
	.then(function (response) // Callback function when response sent from server
	{
		// Check if status code between 200 and 300
		if (response.ok)
		{
			return response.json() // Convert response from server to json

			.then(response =>
			{
				const message = document.querySelector("#message")

				message.innerHTML = response.message

				// Refresh page
				setTimeout(() => {
					top.location = "/products/create"
				}, 1300)
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

/*
*	Edit product page
*/
function getFormattedISO(offsetHours)
{
	// TODO make sure offsetHours is a number

	const d = new Date()

	// https://stackoverflow.com/questions/10830357/javascript-toisostring-ignores-timezone-offset
	const timeZoneOffset = d.getTimezoneOffset() * 60000 //offset in milliseconds

	const offsetDate = new Date((Date.now() - timeZoneOffset))
	offsetDate.setHours(offsetDate.getHours() + offsetHours)

	const offsetDateISO = offsetDate.toISOString()

	return offsetDateISO.slice(0, (offsetDateISO).lastIndexOf(":"))
}

function createDiscount()
{
	const upcomingDiv = document.querySelector("#upcoming_discounts_container")

	if (!upcomingDiv) return

	// Container for the below elements
	const div = document.createElement("div")
	div.classList.add("upcoming_discount")
	div.classList.add("flex_row")

	// Discount amount section
	// Container
	const amountContainer = document.createElement("div")
	amountContainer.classList.add("upcoming_discount_amount_container")
	amountContainer.classList.add("flex_column")

	// Label
	const amountLabel = document.createElement("label")
	amountLabel.innerHTML = "Discount"

	// Input for the discount amount
	const amount = document.createElement("input")
	amount.setAttribute("type", "number")
	amount.name = "upcoming_discount_amount"
	amount.placeholder = "Discount as decimal"
	amount.required = true
	amount.setAttribute("min", "0.01")
	amount.setAttribute("max", "1")
	amount.setAttribute("step", "0.01")
	// Prevent negative numbers
	amount.onkeypress = (event) =>
	{
		return (event.charCode != 8 && event.charCode == 0 || (event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46))
	}
	amountContainer.appendChild(amountLabel)
	amountContainer.appendChild(amount)

	// Start date section
	const startContainer = document.createElement("div")
	startContainer.classList.add("upcoming_discount_amount_container")
	startContainer.classList.add("flex_column")

	// Label
	const startLabel = document.createElement("label")
	startLabel.innerHTML = "Start"

	// Input for start date
	const start = document.createElement("input")
	start.setAttribute("type", "datetime-local")
	start.name = "upcoming_start_date"
	start.required = true

	// Set a min date for start
	start.min = getFormattedISO(1)

	startContainer.appendChild(startLabel)
	startContainer.appendChild(start)

	// End date section
	const endContainer = document.createElement("div")
	endContainer.classList.add("upcoming_discount_amount_container")
	endContainer.classList.add("flex_column")

	// Label
	const endLabel = document.createElement("label")
	endLabel.innerHTML = "End"

	// Input for end date
	const end = document.createElement("input")
	end.setAttribute("type", "datetime-local")
	end.name = "upcoming_end_date"

	endContainer.appendChild(endLabel)
	endContainer.appendChild(end)

	// Delete button
	const deleteButton = document.createElement("button")
	deleteButton.classList.add("delete_button")
	deleteButton.innerHTML = "Delete"
	deleteButton.onclick = () =>
	{
		deleteButton.parentElement.remove()
	}

	div.appendChild(amountContainer)
	div.appendChild(startContainer)
	div.appendChild(endContainer)
	div.appendChild(deleteButton)

	// Get add button
	const addButton = document.querySelector("#upcoming_discounts_container .add_button")

	upcomingDiv.insertBefore(div, addButton)
}

function editProduct(e, id)
{
	e.preventDefault()

	// Make sure start date is 1 hour greater than now
	const startDates = document.querySelectorAll("input[name = 'upcoming_start_date']")

	for (const start of startDates)
	{
		const formattedISO = getFormattedISO(1)

		if (start.value < formattedISO)
		{
			alert(`Discount must start after ${formattedISO.replace("T", " ")}`)
			return
		}
	}

	// Make sure end date is at least 1 hour greater than start date
	const endDates = document.querySelectorAll("input[name = 'upcoming_end_date']")

	for (const end of endDates)
	{
		const formattedISO = getFormattedISO(2)

		if (end.value && end.value < formattedISO)
		{
			alert(`Discount must end at least one hour after start`)
			return
		}
	}

	const form = document.querySelector("#form")

	const formData = new FormData(form)

	const data = {}
	/*
	* Format
	* {
	*	"product_id": 0
	*	"name": "",
	* 	"description": "",
	*	"quantity": "0",
	*	"price": "0.00",
	*	"images": ["", ""] or [],
	*	"warranties": [{"coverage_days": "0 or "", "coverage_info": ""}],
	*	"discounts": [{"discount": "0.00", "start_date": "YYYY-MM-DD HH:MM:SS", "end_date": "YYYY-MM-DD HH:MM:SS" or "" }]
	* }
	*/

	data.product_id = id

	// Info
	data.name = formData.get("name")
	data.description = formData.get("description")
	data.quantity = formData.get("quantity")
	data.price = formData.get("price")

	// Images
	const images = document.getElementsByName("image")

	const imagesArr = []

	Array.from(images).forEach((i) =>
	{
		imagesArr.push(i.value)
	})

	data.images = imagesArr

	// Warranties
	const warrantyDays = document.getElementsByName("coverage_days")
	const warrantyInfo = document.getElementsByName("coverage_info")

	const warrantyArr = []

	for (let i = 0; i < warrantyDays.length; i++)
	{
		warrantyArr.push({
			"coverage_days": warrantyDays[i].value,
			"coverage_info": warrantyInfo[i].value
		})
	}

	data.warranties = warrantyArr

	// Upcoming discounts
	const discountAmounts = document.getElementsByName("upcoming_discount_amount")
	const discountStart = document.getElementsByName("upcoming_start_date")
	const discountEnd = document.getElementsByName("upcoming_end_date")

	const discountArr = []

	for (let i = 0; i < discountAmounts.length; i++)
	{
		// Format end date
		let endDate =  discountEnd[i].value

		if (endDate)
			endDate = endDate.replace("T", " ").concat(":59")

		discountArr.push({
			"discount": discountAmounts[i].value,
			"start_date": discountStart[i].value.replace("T", " ").concat(":59"),
			"end_date": endDate
		})
	}

	data.discounts = discountArr

	fetch(`/products/edit/${id}`, {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "PUT",
		body: JSON.stringify(data)
	})
	.then(function (response) // Callback function when response sent from server
	{
		// Check if status code between 200 and 300
		if (response.ok)
		{
			return response.json() // Convert response from server to json

			.then(response =>
			{
				console.log(response.response)
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
