function handleNegative(event, float = false)
{
	if (float)
		return (event.charCode != 8 && event.charCode == 0 || ((event.charCode >= 48 && event.charCode <= 57)  || event.charCode == 46))

	return (event.charCode != 8 && event.charCode == 0 || (event.charCode >= 48 && event.charCode <= 57))
}

/**
 *
 * @param {*} event
 * @returns True if there is at most one digit in the input and the value is between 1 and 5. False otherwise
 */
function handleRating(event, element = null)
{
	return (event.charCode != 8 && event.charCode == 0 || ((event.charCode >= 49 && event.charCode <= 53))) && (element.value).length < 1
}
