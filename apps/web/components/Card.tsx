import Link from 'next/link';
import React, {ReactElement} from 'react';

type TProps = {
	link: string;
	title: string;
	body: string[];
}

export default function Card(props: TProps): ReactElement {
	const {link, title, body} = props;
	return (
		<Link href={link}>
			<div className={'mb-5 h-full w-full cursor-pointer bg-neutral-100 p-10'}>
				<div className={'flex flex-col pb-6'}>
					<h2 className={'text-3xl font-bold'}>{title}</h2>
				</div>
				<div>
					{body.map((text, index): ReactElement => (
						<p className={'text-neutral-600'} key={`card-body-${index}`}>{text}</p>
					))}
				</div>
			</div> 
		</Link>
	);
}