ignore %r{(^|/)\..+\.sw[a-z]}
ignore %r{.+\.pyc}

guard :shell do
  watch(%r{familytree/.+\.py}) { %x{env/bin/nosetests -vs} }
  watch(%r{tests/helpers/.+\.py}) { %x{env/bin/nosetests -vs} }
  watch(%r{(tests/[^/]+)/__init__\.py}) { |m| %x{env/bin/nosetests -vs #{m[1]}} }
  watch(%r{tests/.+_tests\.py}) { |m| %x{env/bin/nosetests -vs #{m[0]}} }
end
