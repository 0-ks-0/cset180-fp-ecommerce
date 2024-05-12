function handleNegative(event, float = false)
{
	if (float)
		return (event.charCode != 8 && event.charCode == 0 || ((event.charCode >= 48 && event.charCode <= 57)  || event.charCode == 46))

	return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 190
}
