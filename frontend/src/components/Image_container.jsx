import "./../styles/global.css"
import { useEffect, useState } from "react"
import { HOST, PORT } from "./BACKEND_URL"


const Image_container = ({ searchResults }) => {
    const [filenames, setFilenames] = useState([]);
    const BACKEND_URL = HOST + ":" + PORT;
    useEffect(() => {
        if (searchResults !== null) return;

        const fetchFilenames = async () => {
            const response = await fetch(BACKEND_URL + "/get-clusters");
            if (!response.ok) {
                throw new Error(response.status)
            }
            const result = await response.json();
            console.log(result)
            setFilenames(result);
        }
        fetchFilenames();
    }, [searchResults]);

    const imagesToDisplay = searchResults !== null ? searchResults : filenames;

    return (
        <div className="image_container">
            {imagesToDisplay.length > 0 ? (
                imagesToDisplay.map((filename) => (
                    <img src={`${HOST}:${PORT}/image/${filename}`} key={filename} alt={filename} />
                ))
            ) : (
                <p>{searchResults !== null ? "No results found" : "Loading images"}</p>
            )}
        </div>
    )
}

export default Image_container