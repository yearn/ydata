import Link from 'next/link';
import React, {ReactElement} from 'react';
import Image from 'next/image';

type TProps = {
	link: string;
	title: string;
	body: string[];
	image?: string;
	inverseImage?: boolean;
}

export default function Card(props: TProps): ReactElement {
	const {link, title, body} = props;
	return (
		<Link href={link}>
			<div className={'mb-5 h-full w-full cursor-pointer flex h-[300px] '+ (props.inverseImage ? 'flex-row-reverse' : '')}>
				<div className={'h-16'}>
					<Image src={props.image} width={'300px'} height={'300px'} layout={'fixed'}/>
				</div>
				<div className={'h-[300px] w-full bg-neutral-100 p-10'}>
					<div className={'flex flex-col pb-6'}>
						<h2 className={'text-3xl font-bold'}>
							{title}
						</h2>
					</div>
					<div className={'space-y-4'}>
						{body.map((text, index): ReactElement => (
							<p className={'text-neutral-600'} key={`card-body-${index}`}>
								{text}
							</p>
						))}
					</div>
				</div>
			</div> 
		</Link>
	);
}