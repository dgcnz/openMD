const datafolder = "../data/";
const fs = require('fs');
var googleMapsClient = require('@google/maps').createClient({
	key: 'CONSIGUE TU KEY'
});
var filesname=[];
fs.readdir(datafolder, function (err,files){
	files.forEach(file => {
		let tmp=JSON.parse(fs.readFileSync(datafolder+file,'utf8'));
		googleMapsClient.geocode({
			address: tmp.direccion +" "+ tmp.ubicacion
		}, function(err, response) {
			if (!err) {
				console.log(tmp.direccion +" "+ tmp.ubicacion);
				console.log(response.json.results[0].geometry.location);
			}
		});
		filesname.push(
			{
				direcion: tmp.direccion,
				region: tmp.ubicacion
			}
		);
	})
	//console.log(filesname);
})

