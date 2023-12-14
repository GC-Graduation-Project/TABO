import {vextab} from './main.dev.js';


function renderSvg(vextab,data,target) {
	const Renderer = vextab.Vex.Flow.Renderer;

// Create VexFlow Renderer from canvas element with id #boo
const renderer = new Renderer($('#target')[0], Renderer.Backends.SVG);

// Initialize VexTab artist and parser.
const artist = new vextab.Artist(10, 10, 800, { scale: 0.8 });
const tab = new vextab.VexTab(artist);

try {
    tab.parse(data);
    artist.render(renderer);
    return true
	
} catch (e) {
    console.error('error',e);
    return false
}
}
export {renderSvg,vextab}
