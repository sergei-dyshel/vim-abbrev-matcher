require "abbrev_matcher"

function trim5(s)
  return s:match'^%s*(.*%S)' or ''
end

while true do
    local line = io.read()
    if not line then break end
	-- line = trim5(line)
	if abbrev_match(arg[1], line) then
		print(line)
	end
end
