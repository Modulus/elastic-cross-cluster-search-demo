import ec2

def test_has_valid_name():
    instance = {
        "tags" :  [
            {"Key": "Name", "Value": "node-10"}
        ]
    }
    assert ec2.has_valid_name(instance) == True