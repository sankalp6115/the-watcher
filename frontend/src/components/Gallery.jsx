import { useState } from "react"
import Image_container from "./Image_container"
import Searchbar from "./Searchbar"

const Gallery = () => {
    const [searchResults, setSearchResults] = useState(null);

    return (
        <div className="gallery">
            <Searchbar onSearchResults={setSearchResults} />
            <Image_container searchResults={searchResults} />
        </div>
    )
}

export default Gallery