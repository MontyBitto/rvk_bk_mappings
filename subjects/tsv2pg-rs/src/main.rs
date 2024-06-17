use std::collections::HashSet;
use std::io::{self, BufRead};

fn main() {
    let mut unique = HashSet::new();
    let input = io::stdin();
    
    let mut buffer = String::new();
    let stdin = input.lock();
    let mut handle = stdin.lines();

    while let Some(Ok(line)) = handle.next() {
        buffer.clear();
        buffer.push_str(&line);

        let mut data = buffer.split('\t');
        
        if let (Some(ppn), Some(sym), Some(id)) = (data.next(), data.next(), data.next()) {
            if !unique.contains(ppn) {
                if sym == "bk" || sym == "rvk" || sym == "sdnb" {
                    println!("\"{}\" :title ppn:\"{}\"", ppn, ppn);
                    unique.insert(ppn.to_string());
                }
            }
            
            match sym {
                "bk" | "sdnb" => {
                    println!(
                        "\"{}\" -> \"http://uri.gbv.de/terminology/{}/{}\" :subject",
                        ppn, sym, id
                    );
                }
                "rvk" => {
                    println!(
                        "\"{}\" -> \"http://rvk.uni-regensburg.de/nt/{}\" :subject",
                        ppn, id
                    );
                }
                _ => {}
            }
        }
    }
}
