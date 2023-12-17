const { spawn } = require("child_process");

exports.renderMain = async (req, res, next) => {
  try {
    const result = spawn("python", ["hello.py"]);

    let outputData = "";

    result.stdout.on("data", function (data) {
      outputData += data.toString();
    });

    result.on("close", function (code) {
      res.json({ result: outputData });
    });
  } catch (err) {
    console.error(err);
    next(err);
  }
};
