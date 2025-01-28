import hlextend
m = b'This is the end of the message'
sha2 = hlextend.new('sha256')
sha2.hash(m)
print(sha2.hexdigest())
x = b'Or maybe not!'
sha2.extend(sha2.hexdigest(), x)
print(sha2.hexdigest())
sha2 = hlextend.new('sha256')
sha2.hash(m + sha2.padding(len(m)) + x)
print(sha2.hexdigest())
