const datafolder = "../data/";
const fs = require('fs');
var googleMapsClient = require('@google/maps').createClient({
	key: 'AIzaSyCpT0W7a-lzDNG853GPKhgCk2MKl2GO9ME',
	Promise: Promise
});
var files=fs.readdirSync(datafolder)
var data=files.map((file)=>{
	let databotica=JSON.parse(fs.readFileSync(datafolder+file,'utf8'))
	return googleMapsClient.geocode({
		address: databotica.direccion.toLowerCase()+", "+ databotica.ubicacion.toLowerCase()
	})
		.asPromise()
		.then(function (response){
			databotica.coordenadas= response.json.results[0].geometry.location
			return databotica
		})
		.catch(err=>{
			console.log(err);
			return err
		})
})
Promise.all(data)
	.then((d)=>{
		let m=JSON.stringify(d)
		console.log(m);
	})




