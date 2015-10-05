function abbrev_match(abbrev, text)
    if abbrev == '' then
        return true
	end

    if text == '' then
        return false
	end

	local curr = abbrev:sub(1, 1)
	local curr_pat = nil
	if curr:match('%a') then
		curr_pat = string.format('[%s%s]', curr:lower(), curr:upper())
	elseif curr:match('%d') then
		curr_pat =  curr
	else
		curr_pat = '%' .. curr
	end
	local abbrev_rest = abbrev:sub(2)

	if text:sub(1, 1):lower() == curr:lower() and abbrev_match(abbrev_rest, text:sub(2)) then
		return true
	end

	local i = text:find(curr_pat)
	while i ~= nil do

		local two_chars = text:sub(i - 1, i)
		word_boundary = two_chars:match('%U%u') or two_chars:match('%A%l')
			or two_chars:match('%D%d')
		if word_boundary and abbrev_match(abbrev_rest, text:sub(i + 1)) then
			return true
		end

		i = text:find(curr_pat, i + 1)
	end

    return false
end

function abbrev_filter_unite(abbrev, candidates)
	for i = #candidates-1, 0, -1 do
		local word = vim.type(candidates[i]) == 'dict' and
		candidates[i].word or candidates[i]
		if not abbrev_match(abbrev, word) then
			candidates[i] = nil
		end
	end
end
