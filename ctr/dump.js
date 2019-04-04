function DumpObject(obj) {
  return DumpObject2(obj, []);
}
function DumpObject2(obj, seen) {
  var od = new Object;
  var result = "";

  if (seen.indexOf(obj) >= 0) return '<BACKREF>';

  for (var property in obj)
  {
    var value = obj[property];
    if (typeof value == 'string')
      value = "'" + value + "'";
    else if (typeof value == 'object')
    {
      if (value instanceof Array)
      {
        value = "[ " + value + " ]";
      }
      else
      {
        seen.push(obj);
        value = "{ " + DumpObject2(value, seen) + " }";
      }
    }
    result += "'" + property + "' : " + value + ",\n";
  }
  return result.replace(/, $/, "");
}
